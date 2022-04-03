from inspect import isclass


_crs = {}
_dcrs = {}


class _basedcr:
    def __init__(self, cls_or_func, func=None):
        if func is None:
            setattr(self, '_cls' if isclass(cls_or_func) else '_func', cls_or_func)
        else:  # iscr(cls, func) [call outside of class]
            self._register(cls_or_func, func)

    def __call__(self, func):  # iscr(cls)(func) [@iscr(cls), decorator outside of class]
        self._register(self._cls, func)
        return func

    def __set_name__(self, cls, func_name):  # iscr(func) [@iscr, decorator in class]
        setattr(cls, func_name, self._func)
        self._register(cls, lambda c, s: getattr(c, func_name)(s))  # unwrap classmethod

    def _register(self, cls, func, force=True):
        def init_subclass(c, *args, **kwargs):
            cls.__init__subclass__(c, *args, **kwargs)
            # so we can use different dcr on subclass, super dcr is merely the default
            # important detail: __set_name__ is called before __init_subclass__
            self._register(c, func, force=False)

        if force or cls not in self._registry:
            self._registry[cls] = func
            cls.__init_subclass__ = init_subclass  # for yet to be created subclasses
            for subclass in cls.__subclasses__():  # for already existing subclasses
                self._register(subclass, func, force=False)

    @property
    def _registry(self) -> dict:
        raise NotImplementedError


class iscr(_basedcr):
    @property
    def _registry(self):
        return _crs


class isdcr(_basedcr):
    @property
    def _registry(self):
        return _dcrs
