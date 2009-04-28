import ldtp

class Context:
    def __init__(self, window_name):
        self._window_name = window_name
    def __getattr__(self, name):
        obj = getattr(ldtp, name)
        if callable(obj):
            return _ContextFuncWrapper(self._window_name, obj)
        raise AttributeError

class _ContextFuncWrapper:
    def __init__(self, window_name, func):
        self._window_name = window_name
        self._func = func
    def __call__(self, *args, **kwargs):
        return self._func(self._window_name, *args, **kwargs)
