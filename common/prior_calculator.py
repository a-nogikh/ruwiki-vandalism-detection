from dependencies import DepRepo
from features.feature import Feature
import geoip2.errors.GeoIP2Error


class PriorCalculator:

    def __init__(self):
        self.countries = {}
        self.guests = {"vandal": 0, "total": 0}
        self.users = {"vandal": 0, "total": 0}
        self.hours = [{"vandal": 0, "total": 0}] * 24
        self.days = [{"vandal": 0, "total": 0}] * 7
        self.geoip = DepRepo.geoip

    def _append_ip(self, ip: str, vandal: bool):
        if ip is None:
            return
        try:
            info = self.geoip.city(ip)
            country_code = info.country.iso_code
            if country_code is None:
                return

            if country_code not in self.countries:
                self.countries[country_code] = {"vandal": 0, "total": 0}

            self.countries[country_code]['vandal'] += 1 if vandal else 0
            self.countries[country_code]['total'] += 1

        except geoip2.errors.GeoIP2Error:
            pass

    def train_from_list(self, raw):
        for item in raw:
            revs = Feature.revs(item)
            curr = revs["current"]
            if curr is None:
                continue

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

            self.hours[curr["timestamp"].hour()]["vandal"] += vandal_int
            self.hours[curr["timestamp"].hour()]["total"] += 1

    def test(self, item):
        revs = Feature.revs(item)
        if revs["current"] is None:
            raise Exception("Empty revision!")

        curr = revs['current']
        user_score =  (self.guests["vandal"]/self.guests["total"]) \
                        if curr["user"]["id"] is None \
                        else (self.users["vandal"]/self.users["total"])

        # countries
        # normalization

        hour = curr["timestamp"].hour()
        hour_score = self.hours[hour]["vandal"] / self.hours[hour]["total"]

        day = curr["timestamp"].weekday()
        day_score = self.days[day]["vandal"] / self.days[day]["total"]

        return user_score * hour_score * day_score
