from .feature import Feature


class HistoricFeatures(Feature):

    def extract(self, raw):
        revs = raw["revs"]
        revs_p = self.revs(raw)

        anon_c = sum(1 for x in revs if x["user"]["id"] is not None)

        res = {
            'h_prevhrs': 1000 if revs_p['prev_user'] is None else (
                (revs_p['current']['timestamp'] - revs_p['prev_user']['timestamp']).total_seconds() / 86400
            ),
            'h_hasflagged': 1 if any(x['flagged'] for x in revs) else 0,
            'h_guest_p': anon_c / len(revs),
            'h_beenflagged': 1 if any(1 for x in revs[:-1] if x['user']['name'] == revs_p['current']['user']['name']
                                      and x['flagged']) else 0,
            'h_otheredits': sum(1 for x in revs[:-1] if x['user']['name'] == revs_p['current']['user']['name'])
        }

        return res