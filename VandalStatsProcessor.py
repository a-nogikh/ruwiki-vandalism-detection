from pymongo import database, collection
from collections import defaultdict
import pycountry, datetime
import geoip2.database, geoip2.errors
from pytz import timezone

tz_cache = dict()


class VandalStatsProcessor:
    def __init__(self,
                 db: database,
                 geoip: geoip2.database.Reader
                 ):
        self.collection = db.stats  # type: collection.Collection
        self.geoip = geoip
        countries = [x.alpha_2 for x in list(pycountry.countries)]
        self.data = dict(
            (x, {'total': [0] * 24, 'vandal': [0] * 24, 'unknown_total': 0, 'unknown_vandal': 0}) for x in countries)
        self.users = {'total': [0] * 24, 'vandal': [0] * 24}

    @staticmethod
    def get_tz(tz_string: str) -> timezone:
        tz = tz_cache.get(tz_string, None)
        if tz is None:
            tz = timezone(tz_string)
            tz_cache[str] = tz

        return tz

    def add_user(self, tm: datetime.datetime, is_vandal: bool):
        if tm is None:
            return

        self.users['total'][tm.hour] += 1
        self.users['vandal'][tm.hour] += 1 if is_vandal else 0

    def add_ip(self,
               ip: str,
               tm: datetime.datetime,
               is_vandal: bool):
        try:
            if ip is None:
                return  # CHECK THIS CASE

            info = self.geoip.city(ip)
            country_code = info.country.iso_code
            if country_code is None:
                return
            tz_string = info.location.time_zone

            tz = None
            if tz_string is not None:
                tz = self.get_tz(tz_string)

            if tz is None or tm is None:
                self.data[country_code]['unknown_total'] += 1
                self.data[country_code]['unknown_vandal'] += 1 if is_vandal else 0
            else:
                tm_z = tm.astimezone(tz)
                self.data[country_code]['total'][tm_z.hour] += 1
                self.data[country_code]['vandal'][tm_z.hour] += 1 if is_vandal else 0

        except geoip2.errors.GeoIP2Error:
            return

    def save(self):
        self.collection.delete_many({})
        self.collection.insert_one({'guest': self.data, 'users': self.users})
