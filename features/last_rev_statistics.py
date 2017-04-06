from .feature import Feature
import re
from collections import defaultdict

class LastRevStatistics(Feature):

    def extract(self, raw):
        revs = raw["revs"]
        rev = revs[-1]

        title = raw["page"]["title"]
        title_parts = [x.lower() for x in re.findall("[\d\w\-]+", title)]
        collection = raw["rwords"] if "rwords" in raw else {}

        tmp = defaultdict(int)
        for word, diff in collection.items():
            lwr = word.lower()
            if lwr in title_parts:
                tmp[lwr] += diff

        most_extreme = 0
        for val in tmp.values():
            if abs(most_extreme) < abs(val):
                most_extreme = val

        hours_diff = 0

        if rev['user'] is not None:
            if 'reg_date' in rev['user'] and rev['user']['reg_date'] is not None:
                hours_diff = (rev['timestamp'] - rev['user']['reg_date']).total_seconds() / 86400

        res = {
            't_title_diff': most_extreme,
            'lr_minor': 1 if rev["minor"] else 0,
            'lr_guest': 1 if rev["user"]["id"] is None else 0,
            'lr_since_reg': hours_diff
        }

        return res
