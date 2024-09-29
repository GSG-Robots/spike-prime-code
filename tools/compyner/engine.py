import ast
import importlib.util
from pathlib import Path
import re
import sys
import warnings
import random
import string


def name_replacement(
    gr: "GlobalReplacer", name: str, original_node: ast.AST, ctx: ast.expr_context
) -> ast.Attribute:
    if name == gr.compyner.static or name == "ComPYnerBuildTools":
        return ast.copy_location(ast.Name(id=name, ctx=ctx), original_node)
    if gr.use_attr:
        attr = ast.Attribute(
            value=ast.Name(gr.tmp_self, ast.Load()),
            attr=name,
            ctx=ctx,
        )
    else:
        attr = ast.Subscript(
            value=ast.Name(gr.tmp_self, ast.Load()),
            slice=ast.Index(ast.Constant(s=name)),
            ctx=ctx,
        )
    attr = ast.copy_location(attr, original_node)
    return attr


def ast_from_file(file_path: Path) -> ast.Module:
    with file_path.open(encoding="utf-8") as f:
        code = f.read()
    return ast.parse(code)


def path_from_module(module: str) -> Path:
    return Path(importlib.util.find_spec(module).origin)


INTERNALS = ast_from_file(path_from_module("compyner.snippets.internals"))
END = ast_from_file(path_from_module("compyner.snippets.end"))


class ComPYnerBuildTools:
    @staticmethod
    def get_modules_path_glob(
        replacer: "GlobalReplacer", node: ast.Call, /
    ) -> list[ast.AST]:
        args = [replacer.visit(arg) for arg in node.args]
        if len(args) != 1:
            raise ValueError("Import regex takes exaclty one argument")
        if not isinstance(args[0], ast.Constant):
            raise TypeError("The first argument of import_regex must be a constant")
        glob = args[0].value
        files = [file.absolute() for file in Path.cwd().glob(glob)]
        names = [file.with_suffix("").name for file in files]
        elts = []
        for name, file in zip(names, files):
            spec = importlib.util.spec_from_file_location(
                file.with_suffix("").name, file
            )
            do = replacer.compyner._load_module(spec, spec.name)
            if do is False:
                raise ValueError(
                    f"Could not import module {file.relative_to(Path.cwd())} using glob."
                )
            elts.append(
                ast.copy_location(
                    ast.Call(
                        ast.Attribute(
                            ast.Name(replacer.compyner.static, ast.Load()),
                            "get",
                            ast.Load(),
                        ),
                        [ast.Constant(name)],
                        [],
                    ),
                    node,
                )
            )

        return ast.copy_location(
            ast.List(
                elts=elts,
                ctx=ast.Load(),
            ),
            node,
        )


class GlobalFinder(ast.NodeVisitor):
    def __init__(self, explicit_only=False, context=None):
        super().__init__()
        self.globals = []
        self.explicit_only = explicit_only
        self.context = context or []

    def add(self, name):
        if name not in self.globals:
            self.globals.append((name, self.context))

    def visit_Name(self, node: ast.Name):
        if self.explicit_only:
            return
        if isinstance(node.ctx, ast.Store):
            self.add(node.id)

    def visit_Global(self, node):
        for name in node.names:
            self.add(name)

    def visit_FunctionDef(self, node):
        if not self.explicit_only:
            self.add(node.name)
        global_finder = GlobalFinder(
            explicit_only=True, context=self.context + [node.name]
        )
        for subnode in node.body:
            global_finder.visit(subnode)
        for decorator in node.decorator_list:
            self.visit(decorator)
        self.globals.extend(global_finder.globals)

    def visit_ClassDef(self, node):
        if not self.explicit_only:
            self.add(node.name)
        global_finder = GlobalFinder(
            explicit_only=True, context=self.context + [node.name]
        )
        for subnode in node.body:
            global_finder.visit(subnode)
        self.globals.extend(global_finder.globals)

    def visit_Import(self, node: ast.Import):
        if self.explicit_only:
            return
        for alias in node.names:
            self.add((alias.asname or alias.name).split(".")[0])

    def visit_ImportFrom(self, node: ast.ImportFrom):
        if self.explicit_only:
            return
        for alias in node.names:
            self.add(alias.asname or alias.name)


class GlobalReplacer(ast.NodeTransformer):
    def __init__(
        self,
        compyner: "ComPYner",
        globals_,
        parent: "GlobalReplacer" = None,
        context=None,
        tmp_self=None,
        do_position_map=True,
    ):
        super().__init__()
        self.globals = globals_
        self.compyner = compyner
        self.parent = parent
        self.context = context or []
        self.tmp_self = tmp_self or "_comPYned_SELF"
        self.use_attr = False
        self.do_position_map = do_position_map

    def set_line(self, line):
        if not self.do_position_map:
            return ast.Pass()
        return self.compyner.set_line(line)

    def check(self, name, readonly):
        name = name.split(".")[0]
        ctx = self.context.copy()
        while ctx and readonly:
            if (name, ctx) in self.globals:
                return True
            ctx = ctx[:-1]
        return (name, ctx) in self.globals

    def visit_Name(self, node):
        if self.check(node.id, readonly=isinstance(node.ctx, ast.Load)):
            return name_replacement(self, node.id, node, node.ctx)

        return node

    def visit_Global(self, node: ast.Global):
        return ast.Pass()

    def visit_Return(self, node: ast.Return):
        node.value = self.visit(node.value)
        return [
            self.compyner.pop_stack(),
            node,
        ]

    def visit_FunctionDef(self, node):
        sub_replacer = GlobalReplacer(
            self.compyner,
            self.globals,
            self.parent,
            self.context + [node.name],
            self.tmp_self,
            node.name not in ("__exit__", "__del__"),
        )
        node.body = [sub_replacer.visit(n) for n in node.body]
        node.body = [
            self.compyner.push_stack(node.name, node.lineno),
            *node.body,
            self.compyner.pop_stack(),
        ]
        self.use_attr = True
        node.decorator_list = [self.visit(n) for n in node.decorator_list]
        # node.decorator_list += [
        #     ast.Call(
        #         ast.Attribute(ast.Name(self.compyner.static), "has_stack"),
        #         [
        #             ast.Name(self.compyner.stack_var),
        #             ast.List(
        #                 [
        #                     ast.Constant(node.name),
        #                     ast.Name(self.compyner.current_file, ast.Load()),
        #                     ast.Constant(node.lineno),
        #                 ],
        #             ),
        #         ],
        #         [],
        #     )
        # ]
        self.use_attr = False
        node.args = self.visit(node.args) if node.args else None
        if node.returns is not None:
            node.returns = self.visit(node.returns)

        if self.check(node.name, False):
            return [
                node,
                ast.copy_location(
                    ast.Assign(
                        targets=[name_replacement(self, node.name, node, ast.Store())],
                        value=ast.Name(id=node.name, ctx=ast.Load()),
                    ),
                    node,
                ),
            ]
        else:
            return node

    def visit_ClassDef(self, node):
        sub_replacer = GlobalReplacer(
            self.compyner,
            self.globals,
            self.parent,
            self.context + [node.name],
            self.tmp_self,
        )
        node.body = [sub_replacer.visit(n) for n in node.body]
        node.bases = [self.visit(n) for n in node.bases]

        if self.check(node.name, False):
            return [
                node,
                ast.copy_location(
                    ast.Assign(
                        targets=[name_replacement(self, node.name, node, ast.Store())],
                        value=ast.Name(id=node.name, ctx=ast.Load()),
                    ),
                    node,
                ),
            ]
        else:
            return node

    def visit_Import(self, node: ast.Import):
        tmp_name = self.compyner.namer.get_unique_name()
        new_imports = []
        for alias in node.names:
            replace_import = self.compyner.load_module(alias.name, self.parent)
            glob = self.check(alias.asname or alias.name, False)
            parts = (alias.asname or alias.name).split(".")
            for part in range(len(parts) - 1):
                new_imports.append(
                    ast.copy_location(
                        ast.Assign(
                            targets=[
                                name_replacement(
                                    self,
                                    ".".join(parts[: part + 1]),
                                    alias,
                                    ast.Store(),
                                )
                            ],
                            value=ast.Call(
                                ast.Attribute(
                                    ast.Name(self.compyner.static, ast.Load()),
                                    "Module",
                                    ast.Load(),
                                ),
                                [],
                                [],
                            ),
                        ),
                        node,
                    )
                )
            if replace_import:
                new_imports.append(
                    ast.copy_location(
                        ast.Assign(
                            targets=[
                                (
                                    name_replacement(
                                        self,
                                        alias.asname or alias.name,
                                        alias,
                                        ast.Store(),
                                    )
                                    if glob
                                    else ast.copy_location(
                                        ast.Name(
                                            alias.asname or alias.name, ast.Store()
                                        ),
                                        alias,
                                    )
                                )
                            ],
                            value=ast.Call(
                                ast.Attribute(
                                    ast.Name(self.compyner.static, ast.Load()),
                                    "get",
                                    ast.Load(),
                                ),
                                [ast.Constant(replace_import)],
                                [],
                            ),
                        ),
                        node,
                    )
                )
            else:
                new_imports.append(
                    ast.copy_location(
                        ast.Import([ast.alias(alias.name, tmp_name)]), node
                    )
                )
                if alias.asname != tmp_name:
                    new_imports.append(
                        ast.copy_location(
                            ast.Assign(
                                [
                                    (
                                        name_replacement(
                                            self,
                                            alias.asname or alias.name,
                                            alias,
                                            ast.Store(),
                                        )
                                        if glob
                                        else ast.copy_location(
                                            ast.Name(
                                                alias.asname or alias.name, ast.Store()
                                            ),
                                            node,
                                        )
                                    )
                                ],
                                ast.Name(tmp_name, ast.Load()),
                            ),
                            node,
                        )
                    )
        return new_imports

    def visit_Call(self, node: ast.Call):
        node.args = [self.visit(arg) for arg in node.args]
        node.keywords = [self.visit(kwarg) for kwarg in node.keywords]
        if (
            isinstance(node.func, ast.Attribute)
            and isinstance(node.func.value, ast.Name)
            and node.func.value.id == "ComPYnerBuildTools"
        ):
            return getattr(ComPYnerBuildTools, node.func.attr)(self, node)

        node.func = self.visit(node.func)

        return node

    def visit_ImportFrom(self, node: ast.ImportFrom):
        tmp_name = self.compyner.namer.get_unique_name()
        tmp_sub_name = self.compyner.namer.get_unique_name()
        if node.module == "compyner.typehints":
            return ast.Pass()
        new_imports = []
        if node.module is None:
            return self.visit(
                ast.copy_location(
                    ast.Import(
                        [
                            ast.alias(
                                name="." * node.level + alias.name,
                                asname=alias.asname or alias.name,
                            )
                            for alias in node.names
                        ]
                    ),
                    node,
                )
            )
        new_imports.append(
            self.visit_Import(
                ast.copy_location(
                    ast.Import(
                        [
                            ast.alias("." * node.level + node.module, tmp_name),
                        ],
                    ),
                    node,
                )
            )
        )
        if node.names[0].name == "*":
            new_imports.append(
                ast.copy_location(
                    ast.For(
                        target=ast.Name(tmp_sub_name, ast.Store()),
                        iter=ast.Name(tmp_name, ast.Store()),
                        body=[
                            ast.copy_location(
                                ast.Assign(
                                    targets=[
                                        ast.Subscript(
                                            value=ast.Call(
                                                ast.Name("globals", ast.Load()), [], []
                                            ),
                                            slice=ast.Name(tmp_sub_name, ast.Load()),
                                            ctx=ast.Store(),
                                        )
                                    ],
                                    value=ast.Subscript(
                                        ast.Name(tmp_name, ast.Load()),
                                        ast.Name(tmp_sub_name, ast.Load()),
                                        ast.Load(),
                                    ),
                                ),
                                node,
                            )
                        ],
                        orelse=[],
                    ),
                    node,
                ),
            )
            return new_imports
        for alias in node.names:
            glob = self.check(alias.asname or alias.name, False)
            new_imports.append(
                ast.copy_location(
                    ast.Assign(
                        targets=[
                            (
                                name_replacement(
                                    self,
                                    alias.asname or alias.name,
                                    alias,
                                    ast.Store(),
                                )
                                if glob
                                else ast.copy_location(
                                    ast.Name(alias.asname or alias.name, ast.Store()),
                                    alias,
                                )
                            )
                        ],
                        value=ast.Attribute(
                            ast.Name(tmp_name, ast.Load()),
                            # name_replacement(self, tmp_name, node, ast.Load()),
                            alias.name,
                            ast.Load(),
                        ),
                    ),
                    alias,
                )
            )
        return new_imports

    def generic_visit(self, node: ast.stmt) -> list[ast.stmt]:
        if node is None:
            return None
        if isinstance(node, ast.stmt):
            return [self.set_line(node.lineno), super().generic_visit(node)]
        return super().generic_visit(node)


class Namer:
    def __init__(self, prefix=None, random_length=4):
        self.names = {}
        self.prefix = prefix or ""
        self.random_length = random_length
        
    def random_string(self):
        return "".join(random.choices(string.ascii_letters + string.digits + "_", k=self.random_length))

    def get_unique_name(self, name: str = None):
        name = name or ""
        name = re.sub(r"\W", "_", name) + (("_" + self.random_string()) if self.random_length else "")
        self.names[name] = self.names.get(name, 0) + 1
        return self.prefix + name + ("_" + str(self.names[name]) if self.names[name] > 1 else "")


class ComPYner:
    def __init__(
        self,
        exclude=None,
        module_preprocessor=None,
        debug_stack=False,
        debug_line=False,
        split_modules=True,
    ):
        self.exclude = exclude or []
        self.loaded_modules = []
        self.result_module = ast.Module([], [])
        self.module_preprocessor = module_preprocessor or (lambda x, y: x)
        self.namer = Namer()#"_CPYD")
        self.static = self.namer.get_unique_name()
        internals = self.namer.get_unique_name()
        self.result_module.body.append(
            ast.ClassDef(
                name=internals,
                bases=[],
                keywords=[],
                body=[*INTERNALS.body],
                decorator_list=[],
                lineno=0,
                col_offset=0,
                end_lineno=0,
                end_col_offset=0,
            )
        )
        self.result_module.body.append(
            ast.Assign(
                targets=[ast.Name(self.static, ast.Store())],
                value=ast.Call(ast.Name(internals, ast.Load()), [], []),
                lineno=0,
                col_offset=0,
                end_lineno=0,
                end_col_offset=0,
            )
        )
        self.stack_var = self.namer.get_unique_name()
        self.current_file = "<comPYned>"
        if debug_stack:
            self.result_module.body.append(
                ast.Assign(
                    targets=[ast.Name(self.stack_var, ast.Store())],
                    value=ast.List(elts=[], ctx=ast.Load()),
                    lineno=0,
                    col_offset=0,
                    end_lineno=0,
                    end_col_offset=0,
                )
            )
        self.debug_stack = debug_stack
        self.debug_line = debug_line and debug_stack
        self.split_modules = split_modules

    def set_file(self, file):
        if not self.debug_stack:
            return None
        self.current_file = self.namer.get_unique_name()
        return ast.Assign(
            targets=[
                ast.Name(
                    self.current_file,
                    ast.Store(),
                )
            ],
            value=ast.Constant(value=str(file)),
            lineno=0,
            col_offset=0,
            end_lineno=0,
            end_col_offset=0,
        )

    def set_line(self, line):
        if not self.debug_line:
            return None
        return ast.Assign(
            targets=[
                ast.Tuple(
                    [
                        ast.Subscript(
                            ast.Subscript(
                                ast.Name(self.stack_var, ast.Load()),
                                ast.Index(ast.Constant(value=-1)),
                                ast.Load(),
                            ),
                            ast.Index(ast.Constant(value=2)),
                            ast.Store(),
                        ),
                        ast.Subscript(
                            ast.Subscript(
                                ast.Name(self.stack_var, ast.Load()),
                                ast.Index(ast.Constant(value=-1)),
                                ast.Load(),
                            ),
                            ast.Index(ast.Constant(value=1)),
                            ast.Store(),
                        ),
                    ]
                )
            ],
            value=ast.Tuple(
                [ast.Constant(value=line), ast.Name(self.current_file, ast.Load())]
            ),
            lineno=0,
            col_offset=0,
            end_lineno=0,
            end_col_offset=0,
        )

    def push_stack(self, name, lineno=0):
        if not self.debug_stack:
            return None
        return ast.Expr(
            ast.Call(
                ast.Attribute(
                    ast.Name(self.stack_var, ast.Load()),
                    "append",
                    ast.Load(),
                ),
                [
                    ast.List(
                        [
                            ast.Constant(name),
                            ast.Name(self.current_file, ast.Load()),
                            ast.Constant(lineno),
                        ],
                    )
                ],
                [],
            )
        )

    def pop_stack(self):
        if not self.debug_stack:
            return None
        return ast.Expr(
            ast.Call(
                ast.Attribute(
                    ast.Name(self.stack_var, ast.Load()),
                    "pop",
                    ast.Load(),
                ),
                [],
                [],
            )
        )

    def load_module(self, name, parent=None):
        if name.split(".", 1)[0] in self.exclude:
            return False

        try:
            special_spec = importlib.util.find_spec("compyned_polyfills." + name)
            if special_spec:
                return self._load_module(special_spec, name)
        except ModuleNotFoundError:
            pass

        spec = importlib.util.find_spec(name, parent)
        return self._load_module(spec, name)

    def _load_module(self, spec, name=None):
        if not spec:
            raise ModuleNotFoundError(f"Module {name} not found")
        if spec.origin == "built-in":
            warnings.warn(
                f"Module {name} cannot be included: It is a built-in module. Excluded automatically, make sure it exists in the target environment."
            )
            return False
        if not spec.has_location:
            warnings.warn(
                f"Module {name} cannot be included: It does not have a location. Excluded automatically, make sure it exists in the target environment."
            )
            return False
        print(
            f"Loading module {name} as {spec.name} from {spec.origin}", file=sys.stderr
        )

        if spec.name not in self.loaded_modules:
            self.add_module(
                spec.name,
                ast_from_file(Path(spec.origin)),
                spec.parent,
                origin=spec.origin,
            )
        self.loaded_modules.append(spec.name)

        return spec.name

    def add_module(self, name: str, module: ast.Module, parent=None, origin=None):
        module = self.module_preprocessor(module, origin or name)
        gf = GlobalFinder()
        gf.visit(module)
        print(f"Globals in {name}:", file=sys.stderr)
        for glob, target in gf.globals:
            print(f"  {'.'.join(target + [glob])}", file=sys.stderr)
        if not gf.globals:
            print("   (none)", file=sys.stderr)
        tmp_self = self.namer.get_unique_name()
        old_file = self.current_file
        file_set = self.set_file(origin or name)
        tree = GlobalReplacer(self, gf.globals, parent=parent, tmp_self=tmp_self).visit(
            module
        )
        fname = self.namer.get_unique_name(
            "main" if name == "__main__" else "module_" + name
        )
        if self.split_modules:
            self.result_module.body.append(
                ast.FunctionDef(
                    name=fname,
                    args=ast.arguments(
                        args=[],
                        vararg=None,
                        kwonlyargs=[],
                        posonlyargs=[],
                        kw_defaults=[],
                        kwarg=None,
                        defaults=[],
                    ),
                    body=[
                        file_set,
                        self.push_stack(f"<module {name}>"),
                        ast.Assign(
                            targets=[ast.Name(tmp_self, ast.Load())],
                            value=ast.Call(
                                func=ast.Attribute(
                                    ast.Name(self.static, ast.Load()),
                                    "Module",
                                    ast.Load(),
                                ),
                                args=[],
                                keywords=[],
                            ),
                            lineno=0,
                            col_offset=0,
                            end_lineno=0,
                            end_col_offset=0,
                        ),
                        ast.Assign(
                            targets=[
                                ast.Subscript(
                                    value=ast.Name(tmp_self, ast.Load()),
                                    slice=ast.Index(ast.Constant(value="__name__")),
                                    ctx=ast.Store(),
                                ),
                            ],
                            value=ast.Constant(value=name),
                            lineno=0,
                            col_offset=0,
                            end_lineno=0,
                            end_col_offset=0,
                        ),
                        *tree.body,
                        self.pop_stack(),
                        ast.Return(
                            value=ast.Name(
                                tmp_self,
                                ast.Load(),
                                lineno=0,
                                col_offset=0,
                                end_lineno=0,
                                end_col_offset=0,
                            ),
                            lineno=0,
                            col_offset=0,
                            end_lineno=0,
                            end_col_offset=0,
                        ),
                    ],
                    decorator_list=[],
                    lineno=0,
                    col_offset=0,
                    end_lineno=0,
                    end_col_offset=0,
                ),
            )

            assign = ast.Assign(
                targets=[
                    ast.Subscript(
                        value=ast.Attribute(
                            ast.Name(self.static, ast.Load()), "modules", ast.Load()
                        ),
                        slice=ast.Constant(value=name),
                        ctx=ast.Store(),
                    )
                ],
                value=ast.Call(
                    ast.Name(id=fname, ctx=ast.Load()),
                    [],
                    [],
                    lineno=0,
                    col_offset=0,
                    end_lineno=0,
                    end_col_offset=0,
                ),
                lineno=0,
                col_offset=0,
                end_lineno=0,
                end_col_offset=0,
            )
        else:
            self.result_module.body.extend(
                [
                    file_set,
                    self.push_stack(f"<module {name}>"),
                    ast.Assign(
                        targets=[ast.Name(tmp_self, ast.Load())],
                        value=ast.Call(
                            func=ast.Attribute(
                                ast.Name(self.static, ast.Load()),
                                "Module",
                                ast.Load(),
                            ),
                            args=[],
                            keywords=[],
                        ),
                        lineno=0,
                        col_offset=0,
                        end_lineno=0,
                        end_col_offset=0,
                    ),
                    ast.Assign(
                        targets=[
                            ast.Subscript(
                                value=ast.Name(tmp_self, ast.Load()),
                                slice=ast.Index(ast.Constant(value="__name__")),
                                ctx=ast.Store(),
                            ),
                        ],
                        value=ast.Constant(value=name),
                        lineno=0,
                        col_offset=0,
                        end_lineno=0,
                        end_col_offset=0,
                    ),
                    *tree.body,
                    self.pop_stack(),
                ]
            )
            assign = ast.Assign(
                targets=[
                    ast.Subscript(
                        value=ast.Attribute(
                            ast.Name(self.static, ast.Load()), "modules", ast.Load()
                        ),
                        slice=ast.Constant(value=name),
                        ctx=ast.Store(),
                    )
                ],
                value=ast.Name(tmp_self, ast.Load()),
                lineno=0,
                col_offset=0,
                end_lineno=0,
                end_col_offset=0,
            )
        self.current_file = old_file
        if name == "__main__" and (self.debug_stack or self.debug_line):
            error_name = self.namer.get_unique_name()
            self.result_module.body.append(
                ast.Try(
                    body=[assign],
                    handlers=[
                        ast.ExceptHandler(
                            type=ast.Name("Exception", ast.Load()),
                            name=error_name,
                            body=[
                                ast.Expr(
                                    ast.Call(
                                        ast.Name("print", ast.Load()),
                                        [
                                            # ast.Constant("Error at: "),
                                            # ast.Subscript(
                                            #     ast.Name(self.stack_var, ast.Load()),
                                            #     ast.Index(ast.Constant("file")),
                                            #     ast.Load(),
                                            # ),
                                            # ast.Constant(":"),
                                            # ast.Subscript(
                                            #     ast.Name(self.metadata_var, ast.Load()),
                                            #     ast.Index(ast.Constant("line")),
                                            #     ast.Load(),
                                            # ),
                                            # ast.Subscript(
                                            #     ast.Name(self.metadata_var, ast.Load()),
                                            #     ast.Index(ast.Constant("stack")),
                                            #     ast.Load(),
                                            # ),
                                            ast.Name(self.stack_var, ast.Load()),
                                        ],
                                        [
                                            # ast.keyword(
                                            #     arg="sep", value=ast.Constant("")
                                            # ),
                                        ],
                                        lineno=0,
                                        col_offset=0,
                                        end_lineno=0,
                                        end_col_offset=0,
                                    ),
                                    lineno=0,
                                    col_offset=0,
                                    end_lineno=0,
                                    end_col_offset=0,
                                ),
                                ast.Raise(
                                    exc=ast.Name(error_name, ast.Load()),
                                    cause=None,
                                    lineno=0,
                                    col_offset=0,
                                    end_lineno=0,
                                    end_col_offset=0,
                                ),
                            ],
                        )
                    ],
                    orelse=[],
                    finalbody=[],
                    lineno=0,
                    col_offset=0,
                    end_lineno=0,
                    end_col_offset=0,
                )
            )
            return
        self.result_module.body.append(assign)

    def compyne(self):
        self.result_module.body.extend(END.body)
        return ast.unparse(self.result_module)
