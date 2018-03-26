import collections
import logging
import operator

import requests
import tabulate
from fire import Fire

logger = logging.getLogger()

server = collections.namedtuple('server', ('city', 'country', 'hostname', 'capacity', 'online'))


class IPVanish:
    url = 'https://www.ipvanish.com/api/servers.geojson'
    fields = server._fields

    def __init__(self, countries=None, cities=None, retry_count=5, sort_by='capacity', ascending=True):
        self.countries = countries
        self.cities = cities
        self.retry_count = retry_count
        self.sort_by = sort_by
        self.ascending = ascending
        self._raw = None
        self._data = None

    @property
    def raw(self):
        for _ in range(self.retry_count):
            resp = requests.get(self.url)
            try:
                self._raw = resp.json()
                return self._raw
            except Exception as e:
                logger.warning(e)

    @property
    def data(self):
        if not self._data:
            self._data = [server(d['properties'][f] for f in self.fields) for d in self.raw]
            if self.countries is not None:
                self._data = self.filter(data=self._data, key='country', value=self.countries)
            if self.cities is not None:
                self._data = self.filter(data=self._data, key='city', value=self.cities)
            self._data = sorted(self._data, key=operator.itemgetter(self.sort_by), reverse=not self.ascending)
        return self._data

    def head(self, n=1):
        return self.data[:n]

    def filter(self, data, key, value):
        if isinstance(value, str):
            data = [d for d in data if d[key] == value]
        elif isinstance(value, (list, tuple)):
            data = [d for d in data if d[key] in value]
        else:
            raise NotImplementedError()
        return data

    def __repr__(self):
        return tabulate.tabulate(map(lambda x: x.values(), self.head(n=5)), headers=self.fields)


def main():
    Fire(IPVanish)


if __name__ == '__main__':
    main()
