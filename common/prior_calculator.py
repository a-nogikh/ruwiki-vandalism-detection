from dependencies import DepRepo
from features.feature import Feature
import geoip2.database, geoip2.errors


class PriorCalculator:

    def __init__(self):
        self.countries = {}
        self.guests = {"vandal": 0, "total": 0}
        self.users = {"vandal": 0, "total": 0}
        self.hours = [{"vandal": 0, "total": 0}] * 24
        self.days = [{"vandal": 0, "total": 0}] * 7
        self.geoip = DepRepo.geoip()

    def get_country(self, ip: str):
        if ip is None:
            return
        try:
            info = self.geoip.city(ip)
            country_code = info.country.iso_code
            if country_code is None:
                return
            return country_code
        except geoip2.errors.GeoIP2Error:
            return "UNK"

    def _append_ip(self, ip: str, vandal: bool):
        country_code = self.get_country(ip)

        if country_code not in self.countries:
            self.countries[country_code] = {"vandal": 0, "total": 0}

        self.countries[country_code]['vandal'] += 1 if vandal else 0
        self.countries[country_code]['total'] += 1

    def train_one(self,raw):
        revs = Feature.revs(raw)
        curr = revs["current"]
        if curr is None:
            return

        vandal_int = 1 if raw["vandal"] else 0
        if curr["user"]["id"] is None:
            self._append_ip(curr["user"]["name"], raw["vandal"])
            self.guests["total"] += 1
            self.guests["vandal"] += vandal_int
        else:
            self.users["total"] += 1
            self.users["vandal"] += vandal_int

        self.days[curr["timestamp"].weekday()]["vandal"] += vandal_int
        self.days[curr["timestamp"].weekday()]["total"] += 1

        self.hours[curr["timestamp"].hour]["vandal"] += vandal_int
        self.hours[curr["timestamp"].hour]["total"] += 1

    def train_from_list(self, raw):
        for item in raw:
            self.train_one(item)

    def test(self, item):
        revs = Feature.revs(item)
        if revs["current"] is None:
            raise Exception("Empty revision!")

        curr = revs['current']
        avg_score =  (self.guests["vandal"]/self.guests["total"]) \
                        if curr["user"]["id"] is None \
                        else (self.users["vandal"]/self.users["total"])
        user_score = 0
        if curr["user"]["id"] is None:
            country_code = self.get_country(curr["user"]["name"])
            if country_code not in self.countries or self.countries[country_code]["vandal"] < 10:
                user_score = avg_score
            else:
                user_score = self.countries[country_code]["vandal"] / self.countries[country_code]["total"]
        else:
            user_score = avg_score

        hour = curr["timestamp"].hour
        hour_score = self.hours[hour]["vandal"] / self.hours[hour]["total"]

        day = curr["timestamp"].weekday()
        day_score = self.days[day]["vandal"] / self.days[day]["total"]

        return 1 # hour_score * day_score
