from .feature import Feature
import re
from collections import defaultdict
from common.user_flags import UserFlags
from dependencies import DepRepo


class LastRevStatistics(Feature):
    flags = DepRepo.flags()
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
        adv_flag = 0

        if rev['user'] is not None:
            if rev['user']['id'] is not None:
                flags = self.flags.get_flags(rev['user']['id']) or []
                adv_flag = 1 if 'autoconfirmed' in flags or 'uploader' in flags else 0

            if 'reg_date' in rev['user'] and rev['user']['reg_date'] is not None:
                hours_diff = (rev['timestamp'] - rev['user']['reg_date']).total_seconds() / 86400

        res = {
            't_title_diff': most_extreme,
            'lr_minor': 1 if rev["minor"] else 0,
            'lr_guest': 1 if rev["user"]["id"] is None else 0,
            'lr_since_reg': hours_diff,
            'lr_hour': rev['timestamp'].hour + rev['timestamp'].minute/60,
            'lr_wday': rev["timestamp"].weekday(),
            'lr_usr_contr': rev['user']['contrib_total'] if 'contrib_total' in rev['user'] else 0,
            'lr_usr_contr_pg': rev['user']['contrib_pages'] if 'contrib_pages' in rev['user'] else 0,
            'lr_advflag' : adv_flag
        }

        return res
