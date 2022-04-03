from dataclasses import dataclass
from datetime import date
from typing import Optional
from pydcr import iscr, isdcr, cr, _dcrs
from yarl import URL


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
        return cls(spl[0][:-1], date.fromisoformat(spl[-1]))


@dataclass
class Band:
    name: str
    members: list[BandMember]
    website: Optional[URL] = None
    _helper = 'default'


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
    print(cr(band))
    print(_dcrs[BandMember](BandMember, serialized['members'][0]))
    # assert dcr(Band, serialized) == band
    # assert cr(band) == serialized


if __name__ == '__main__':
    main()
