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

        res = {
            't_title_diff': most_extreme,
            'lr_minor': 1 if rev["minor"] else 0
        }

        return res
