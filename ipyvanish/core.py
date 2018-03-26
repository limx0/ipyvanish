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

    def __init__(self, countries=None, cities=None, count=5, sort_by='capacity', ascending=True, retry_count=5, values_only=False):
        self.countries = countries
        self.cities = cities
        self.count = count
        self.sort_by = sort_by
        self.ascending = ascending
        self.retry_count = retry_count
        self.values_only = values_only

    def _request(self):
        for _ in range(self.retry_count):
            resp = requests.get(self.url)
            try:
                return resp.json()
            except Exception as e:
                logger.warning(e)

    def _filter(self, data, key, value):
        if isinstance(value, str):
            data = [d for d in data if getattr(d, key) == value]
        elif isinstance(value, (list, tuple)):
            data = [d for d in data if getattr(d, key) in value]
        else:
            raise NotImplementedError()
        return data

    def _format(self, data):
        if self.values_only:
            return tabulate.tabulate(data[:self.count], tablefmt='plain')
        else:
            return tabulate.tabulate(data[:self.count], headers=self.fields)

    def poll(self):
        raw = self._request()

        data = [server(*[d['properties'][f] for f in self.fields]) for d in raw]
        if self.countries is not None:
            data = self._filter(data=data, key='country', value=self.countries)
        if self.cities is not None:
            data = self._filter(data=data, key='city', value=self.cities)

        data = sorted(data, key=operator.attrgetter(self.sort_by), reverse=not self.ascending)
        return self._format(data)


def main():
    Fire(IPVanish)


if __name__ == '__main__':
    main()
