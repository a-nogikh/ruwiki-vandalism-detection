from .feature import Feature
import re
from common.utils import strip_comment
from urllib.parse import urlparse
from collections import Counter


cmpl = re.compile(r"(https?:\/\/(?:www\.|(?!www))[a-zA-Z0-9][a-zA-Z0-9-]+[a-zA-Z0-9]\.[^\s]{2,}|www\.[a-zA-Z0-9][a-zA-Z0-9-]+[a-zA-Z0-9]\.[^\s]{2,}|https?:\/\/(?:www\.|(?!www))[a-zA-Z0-9]\.[^\s]{2,}|www\.[a-zA-Z0-9]\.[^\s]{2,})")

class UrlStatisticsFeatures(Feature):

    def extract(self, raw):
        revs = self.revs(raw)
        curr_text = (revs["current"]['text'] if revs['current'] is not None else '') or ''
        prev_text = (revs['prev_user']['text'] if revs['prev_user'] is not None else '') or ''
        last_rev = self.last_rev(raw)
        comment = strip_comment(last_rev["comment"])

        prev_urls = {x for x in cmpl.findall(prev_text)}
        curr_urls = [x for x in cmpl.findall(curr_text)]

        new_urls = [x for x in curr_urls if x not in prev_urls]
        try:
            new_domains = [urlparse(x).netloc for x in new_urls]
        except Exception:
            new_domains = new_urls

        min_added = 0 if len(new_domains) == 0 else min(list(Counter(new_domains).values()))
        return {
            "url_minadded": min_added,
            "url_diversity": 1 if len(new_urls) == 0 else len(new_urls) / len(set(new_domains)),
            "url_diff": len(curr_urls) - len(prev_urls),
            "url_comment": 1 if any(x for x in cmpl.findall(comment)) else 0
        }
