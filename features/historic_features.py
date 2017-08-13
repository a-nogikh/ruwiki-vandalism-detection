from .feature import Feature
from common.revision_tools import RevisionTools

class HistoricFeatures(Feature):

    def extract(self, raw):
        revs = raw["revs"]
        for i in reversed(range(0, len(revs) - 1)):
            if i == 0:
                continue

            comment = revs[i]["comment"]
            if RevisionTools.is_reverting(comment):
                cmp = revs[i-1]["user"]["name"]
                for j in reversed(range(0, i)):
                    if revs[j]["user"]["name"] != cmp:
                        break

                    revs[j]["reverted"] = True
                continue

            cancels_id = RevisionTools.cancels_id(comment)
            if cancels_id is not None:
                for j in range(0, i):
                    if revs[j]["id"] == cancels_id:
                        revs[j]["cancelled"] = True
                        break

        revs_p = self.revs(raw)



        anon_c = sum(1 for x in revs if x["user"]["id"] is not None)
        other_cnt = sum(1 for x in revs[:-1] if x['user']['name'] == revs_p['current']['user']['name'])

        res = {
            'h_prevhrs': 1000 if revs_p['prev_user'] is None else (
                (revs_p['current']['timestamp'] - revs_p['prev_user']['timestamp']).total_seconds() / 86400
            ),
            'h_beencancelled': 1 if any(1 for x in revs if x['user']['name'] == revs_p['current']['user']['name']
                                      and ('reverted' in x or 'cancelled' in x ) ) else 0,
            'h_hasflagged': 1 if any(x['flagged'] for x in revs) else 0,
            'h_guest_p': anon_c / len(revs),
            'h_beenflagged': 1 if any(1 for x in revs[:-1] if x['user']['name'] == revs_p['current']['user']['name']
                                      and x['flagged']) else 0,
            'h_otheredits': other_cnt,
            'h_otheredits_p': other_cnt / len(revs)
        }

        return res
