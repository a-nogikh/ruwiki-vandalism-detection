from .feature import Feature


class HistoricFeatures(Feature):

    def extract(self, raw):
        revs = raw["revs"]
        revs_p = self.revs(raw)

        res = {
            'h_prevhrs': 1000 if revs_p['prev_user'] is None else (
                (revs_p['current']['timestamp'] - revs_p['prev_user']['timestamp']).total_seconds() / 86400
            ),
            'h_hasflagged': 1 if any(x['flagged'] for x in revs) else 0
        }

        return res