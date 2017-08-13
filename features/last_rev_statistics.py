from .feature import Feature
import re
from collections import defaultdict
from common.utils import strip_accents
from dependencies import DepRepo
from common.revision_tools import RevisionTools


class LastRevStatistics(Feature):
    flags = DepRepo.flags()
    def extract(self, raw):
        revs = raw["revs"]
        rev = revs[-1]

        comment_text = rev["comment"]

        title = strip_accents(raw["page"]["title"])
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

        revs2 = Feature.revs(raw)
        curr_text = (revs2["current"]['text'] if revs2['current'] is not None else '') or ''
        lower_txt = curr_text.lower()

        hours_diff = 0
        adv_flag = 0

        if rev['user'] is not None:
            if rev['user']['id'] is not None:
                flags = self.flags.get_flags(rev['user']['id']) or []
                adv_flag = 1 if 'autoconfirmed' in flags or 'uploader' in flags else 0

            if 'reg_date' in rev['user'] and rev['user']['reg_date'] is not None:
                hours_diff = (rev['timestamp'] - rev['user']['reg_date']).total_seconds() / 3600

        hours_since_last = 0
        if revs2['prev_user'] is not None:
            hours_since_last = (revs2['current']['timestamp'] - revs2['prev_user']['timestamp']).total_seconds() / 3600

        usr_contr = rev['user']['contrib_total'] if 'contrib_total' in rev['user'] else 0
        usr_contr_pg = rev['user']['contrib_pages'] if 'contrib_pages' in rev['user'] else 0

        #if rev["user"]["id"] is None:
        ##    usr_contr_pg = 0
        #   usr_contr = 0

        res = {
            't_title_diff': most_extreme,
            'lr_minor': 1 if rev["minor"] else 0,
            'lr_guest': 1 if rev["user"]["id"] is None else 0,
            'lr_since_reg': hours_diff,
            'lr_since_last': hours_since_last,
            'lr_hour': rev['timestamp'].hour + rev['timestamp'].minute/60,
            'lr_wday': rev["timestamp"].weekday(),
            'lr_usr_contr': usr_contr,
            'lr_usr_contr_pg': usr_contr_pg,
            'lr_usr_contr_rel': 1 if usr_contr_pg == 0 else usr_contr / usr_contr_pg,
            'lr_advflag' : adv_flag,
            'lr_is_redirect' : 1 if '#redirect' in lower_txt or '#перенаправление' in lower_txt else 0,
            'lr_is_cancelling' : 1 if (RevisionTools.cancels_id(comment_text) is not None  or RevisionTools.is_reverting(comment_text)) else 0
        }

        return res
