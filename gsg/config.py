class _config:
    """Configuration object"""
    def __init__(self, **kwargs):
        self._parent = config
        self._dict = kwargs

    def __enter__(self):
        global config
        config = self

    def __exit__(self, exc_type, exc_val, exc_tb):
        global config
        config = self._parent

    def __getattr__(self, name):
        if name.startswith("_"):
            return getattr(self, name)
        if name in self._dict:
            return self._dict[name]
        if self._parent is not None:
            return getattr(self._parent, name)
        raise AttributeError(name)

    def __call__(self, **kwargs):
        return _config(**kwargs)


# For typehints
class Config:
    """Configuration object"""

    test: int
    
    def __enter__(self): ...
    def __exit__(self, exc_type, exc_val, exc_tb): ...
    def __call__(self, test: int | None = None): ...


config = None
config: Config = _config(test=1)