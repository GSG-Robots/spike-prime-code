class _ConfigContext:
    def __init__(self, _parent: "ConfigBase", **kwargs):
        self._parent = _parent
        self._changes = kwargs

    def __enter__(self):
        self._parent._layers.append(self._changes)

    def __exit__(self, exc_type, exc_val, exc_tb):
        self._parent._layers.pop(-1)


class ConfigBase:
    """Configuration object"""

    def __init__(self, **kwargs):
        self._layers = [kwargs]

    @property
    def _dict(self):
        return {key: value for layer in self._layers for key, value in layer.items()}

    def __getattr__(self, name):
        if name.startswith("_"):
            return getattr(self, name)
        _dict = self._dict
        if name in _dict:
            return _dict[name]
        raise AttributeError(name)

    def __call__(self, **kwargs):
        return _ConfigContext(self, **kwargs)
