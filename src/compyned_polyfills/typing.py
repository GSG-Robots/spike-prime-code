class _Subscriptable:
    def __getitem__(self, sub):
        return None
_SubSingleton = _Subscriptable()
def TypeVar(new_type, *types):
    return None
TYPE_CHECKING = False
Any = object
Text = str
NoReturn = None
ClassVar = object
Union = _SubSingleton
Optional = _SubSingleton
Generic = _SubSingleton
NamedTuple = _SubSingleton
Hashable = object
Awaitable = object
Coroutine = object
AsyncIterable = object
AsyncIterator = object
Iterable = object
Iterator = object
Reversible = object
Sized = object
Container = object
Collection = object
Callable = _SubSingleton
AbstractSet = _SubSingleton
MutableSet = _SubSingleton
Mapping = _SubSingleton
MutableMapping = _SubSingleton
Sequence = _SubSingleton
MutableSequence = _SubSingleton
ByteString = object
Tuple = _SubSingleton
List = _SubSingleton
Deque = object
Set = _SubSingleton
FrozenSet = _SubSingleton
MappingView = object
KeysView = object
ItemsView = object
ValuesView = object
ContextManager = object
AsyncContextManager = object
Dict = _SubSingleton
DefaultDict = _SubSingleton
Counter = object
ChainMap = object
Generator = object
AsyncGenerator = object
Type = object
IO = _SubSingleton
TextIO = IO[str]
BinaryIO = IO[bytes]
AnyStr = TypeVar("AnyStr", str, bytes)
def cast(typ, val):
    return val
def _overload_dummy(*args, **kwds):
    """Helper for @overload to raise when called."""
    raise NotImplementedError(
        "You should not call an overloaded function. "
        "A series of @overload-decorated functions "
        "outside a stub module should always be followed "
        "by an implementation that is not @overload-ed."
    )
def overload(fun):
    return _overload_dummy
