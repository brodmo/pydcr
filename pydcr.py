from dataclasses import is_dataclass
from inspect import isclass


_crs = {}
_dcrs = {}


def cr(obj):
    t = type(obj)
    if t in _crs:
        return _crs[t](obj)
    if any(t is c for c in (list, tuple, set)):
        return t(cr(o) for o in obj)
    if t is dict:
        return {cr(k): cr(v) for k, v in obj.items()}
    if t.__module__ == 'builtins':
        return obj
    if is_dataclass(t):
        return {n: cr(v) for n, v in vars(obj).items()}
    raise TypeError(f'cr not defined for type {t}')


def dcr(cls, obj):
    pass  # todo list, tuple, set, dict, Optional, Union
    if isinstance(obj, cls):
        return obj


class _basedcr:
    def __init__(self, cls_or_func, func=None):
        if func is None:
            setattr(self, '_cls' if isclass(cls_or_func) else '_func', cls_or_func)
        else:  # iscr(cls, func) [call outside of class]
            self._register(cls_or_func, func)

    def __call__(self, func):  # iscr(cls)(func) [@iscr(cls), decorator outside of class]
        self._register(self._cls, func)
        return func

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
    def __set_name__(self, cls, func_name):  # iscr(func) [@iscr, decorator in class]
        setattr(cls, func_name, self._func)
        self._register(cls, lambda i: getattr(i, func_name)())  # unwrap instance method

    @property
    def _registry(self):
        return _crs


class isdcr(_basedcr):
    def __set_name__(self, cls, func_name):  # iscr(func) [@iscr, decorator in class]
        setattr(cls, func_name, self._func)
        self._register(cls, lambda c, s: getattr(c, func_name)(s))  # unwrap classmethod

    @property
    def _registry(self):
        return _dcrs
