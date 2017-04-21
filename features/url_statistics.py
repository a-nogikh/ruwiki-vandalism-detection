from .feature import Feature
import re
from collections import defaultdict


cmpl = re.compile(r"(https?:\/\/(?:www\.|(?!www))[a-zA-Z0-9][a-zA-Z0-9-]+[a-zA-Z0-9]\.[^\s]{2,}|www\.[a-zA-Z0-9][a-zA-Z0-9-]+[a-zA-Z0-9]\.[^\s]{2,}|https?:\/\/(?:www\.|(?!www))[a-zA-Z0-9]\.[^\s]{2,}|www\.[a-zA-Z0-9]\.[^\s]{2,})")

class UrlStatisticsFeatures(Feature):

    def extract(self, raw):
        revs = self.revs(raw)
        curr_text = (revs["current"]['text'] if revs['current'] is not None else '') or ''
        prev_text = (revs['prev_user']['text'] if revs['prev_user'] is not None else '') or ''

        prev_urls = [x for x in cmpl.findall(prev_text)]
        curr_urls = [x for x in cmpl.findall(curr_text)]

        return {
            "url_diff": len(curr_urls) - len(prev_urls)
        }
