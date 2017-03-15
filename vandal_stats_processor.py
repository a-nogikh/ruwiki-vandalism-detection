from pymongo import database, collection
from collections import defaultdict
import pycountry, datetime
import geoip2.database, geoip2.errors
from pytz import timezone

tz_cache = dict()

TOTAL_TIMESPAN_LEN = (int)((1440 / 5) * 7)


class VandalStatsProcessor:
    def __init__(self,
                 db: database,
                 geoip: geoip2.database.Reader
                 ):
        self.collection = db.stats  # type: collection.Collection
        self.geoip = geoip

        countries = [x.alpha_2 for x in list(pycountry.countries)]
        self.data = dict(
            (x, {
                'total': [0] * 24,
                'vandal': [0] * 24,
                'unknown_total': [0] * 24,
                'unknown_vandal': [0] * 24,
                'days_total': [0] * 7,
                'days_vandal': [0] * 7
            }) for x in countries)

        self.errors = {
            'no_country': {
                'vandal': [0]*24,
                'total': [0]*24
            }
        }

        self.users = {
            'total': [0] * 24,
            'vandal': [0] * 24,
            'days_total': [0] * 7,
            'days_vandal': [0] * 7
        }

        self.till_removed = {
            'cancel': {
                'list': [0] * TOTAL_TIMESPAN_LEN,
                'longer': 0
            },
            'rollback': {
                'list': [0] * TOTAL_TIMESPAN_LEN,
                'longer': 0
            }
        }

        obj = self.collection.find_one()
        if obj is None:
            return

        self.data = VandalStatsProcessor.merge(self.data,obj['guest'])
        self.users = VandalStatsProcessor.merge(self.users,obj['users'])
        self.till_removed = VandalStatsProcessor.merge(self.till_removed,obj['till_removed'])
        self.errors['no_country'] =VandalStatsProcessor.merge(self.errors['no_country'],obj['guest_no_country'])

    @staticmethod
    def get_tz(tz_string: str) -> timezone:
        tz = tz_cache.get(tz_string, None)
        if tz is None:
            tz = timezone(tz_string)
            tz_cache[str] = tz

        return tz

    def add_time_diff(self, is_cancel: bool, tm_rev: datetime.datetime, tm_cancel: datetime.datetime):
        diff = tm_cancel - tm_rev
        diff_minutes = int((diff.days * 86400 + diff.seconds) / (60*5))
        type = 'cancel' if is_cancel else 'rollback'
        if diff_minutes < TOTAL_TIMESPAN_LEN:
            self.till_removed[type]['list'][diff_minutes] += 1
        else:
            self.till_removed[type]['longer'] += 1

    def add_user(self, tm: datetime.datetime, is_vandal: bool):
        if tm is None:
            return

        vandal = 1 if is_vandal else 0
        self.users['days_total'][tm.weekday()] += 1
        self.users['days_vandal'][tm.weekday()] += vandal
        self.users['total'][tm.hour] += 1
        self.users['vandal'][tm.hour] += vandal

    def add_ip(self,
               ip: str,
               tm: datetime.datetime,
               is_vandal: bool):

        vandal = 1 if is_vandal else 0
        try:
            if ip is None or tm is None:
                return

            info = self.geoip.city(ip)
            country_code = info.country.iso_code

            if country_code is None or country_code not in self.data:
                self.errors['no_country']['vandal'][tm.hour] += vandal
                self.errors['no_country']['total'][tm.hour] += vandal
                return

            tz_string = info.location.time_zone

            tz = None
            if tz_string is not None:
                tz = self.get_tz(tz_string)

            if tz is None:
                self.data[country_code]['unknown_total'][tm.hour] += 1
                self.data[country_code]['unknown_vandal'][tm.hour] += vandal
            else:
                tm_z = tm.astimezone(tz)
                self.data[country_code]['days_total'][tm_z.weekday()] += 1
                self.data[country_code]['days_vandal'][tm_z.weekday()] += vandal
                self.data[country_code]['total'][tm_z.hour] += 1
                self.data[country_code]['vandal'][tm_z.hour] += vandal

        except geoip2.errors.GeoIP2Error:
            self.errors['no_country']['vandal'][tm.hour] += vandal
            self.errors['no_country']['total'][tm.hour] += vandal
            return


    # http://stackoverflow.com/questions/7204805/dictionaries-of-dictionaries-merge
    @staticmethod
    def merge(a, b, path=None):
        "merges b into a"
        if path is None: path = []
        for key in b:
            if key in a:
                if isinstance(a[key], dict) and isinstance(b[key], dict):
                    VandalStatsProcessor.merge(a[key], b[key], path + [str(key)])
                elif a[key] == b[key]:
                    pass  # same leaf value
                else:
                    a[key] = b[key]
            else:
                a[key] = b[key]
        return a

    def clear(self):
        self.collection.delete_many({})

    def save(self):

        newobj = {
            'guest': self.data,
            'guest_no_country': self.errors['no_country'],
            'users': self.users,
            'till_removed': self.till_removed
        }

        self.collection.delete_many({})
        self.collection.insert_one(newobj)
