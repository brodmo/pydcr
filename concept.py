from dataclasses import dataclass
from datetime import date
from inspect import isclass
from typing import Optional
# from pydcr import cr, dcr, iscr, isdcr
from yarl import URL


class _basedcr:
    def __init__(self, cls_or_func, func=None):
        if func is None:
            setattr(self, 'cls' if isclass(cls_or_func) else 'func', cls_or_func)
        else:
            self._register(cls_or_func, func)  # iscr(cls, func) [call outside of class]

    def __call__(self, func):
        self._register(self.cls, func)  # iscr(cls)(func) [@iscr(cls), decorator outside of class]
        return func

    def __set_name__(self, cls, func_name):
        self._register(cls, self.func)  # iscr(func) [@iscr, decorator in class]
        setattr(cls, func_name, self.func)

    def _register(self, cls, func):
        raise NotImplementedError


class iscr(_basedcr):
    def _register(self, cls, func):
        print('cr', cls, func)


class isdcr(_basedcr):
    def _register(self, cls, func):
        print('dcr', cls, func)


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
    # assert dcr(serialized) == band
    # assert cr(band) == serialized


if __name__ == '__main__':
    main()
