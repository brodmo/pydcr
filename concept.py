from dataclasses import dataclass
from datetime import date
from inspect import isclass
from typing import Optional
# from pydcr import cr, dcr, iscr, isdcr
from yarl import URL


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


@dataclass
class BandMember:
    name: str
    birthday: date

    @iscr
    def __str__(self):
        return f'{self.name}, born {self.birthday}'

    @isdcr
    @classmethod
    def from_str(cls, string):
        spl = string.split()
        return cls(spl[0], date.fromisoformat(spl[-1]))


@dataclass
class Band:
    Name: str
    members: list[BandMember]
    website: Optional[URL] = None


@iscr(URL)
def serialize_url(url):  # alternatively: iscr(URL, str)
    return str(url)


@isdcr(URL)
def deserialize_url(cls, string):  # alternatively: isdcr(URL, lambda c, s: c(s))
    return cls(string)


def main():
    serialized = {
      'name': 'New Order',
      'members': [
        'Summer, born on 1956-01-04', 
        'Morris, born on 1957-10-28', 
        'Gilbert, born on 1961-01-27'
      ],
      'website': 'https://www.neworder.com'
    }
    members = list(map(BandMember.from_str, serialized['members']))
    url = deserialize_url(URL, serialized['website'])
    band = Band(serialized['name'], members, url)
    # assert dcr(Band, serialized) == band
    # assert cr(band) == serialized


if __name__ == '__main__':
    main()
