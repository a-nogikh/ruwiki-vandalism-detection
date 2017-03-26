from .feature import Feature


class HistoricFeatures(Feature):

    def extract(self, raw):
        revs = raw["revs"]
        return {}