import requests


class MediaWikiApiResourceInaccessible(Exception):
    pass

class MediaWikiApiNetworkingException(MediaWikiApiResourceInaccessible):
    pass

class MediaWikiApi:
    def __init__(self, base_path: str):
        self.base_path = base_path

    def query_revisions_by_ids(self, page_ids: int, rvprop: list):
        return self._get_query({
            "action": "query",
            "format": "json",
            "prop": "revisions",
            "revids": "|".join(str(x) for x in page_ids),
            "rvprop": "|".join(str(x) for x in rvprop)
        })

    def _get_query(self, params: dict) -> dict:
        try:
            r = requests.get(self.base_path, params)
            r.raise_for_status()
            
            return r.json()["query"]
        except requests.exceptions.HTTPError as errh:
            raise MediaWikiApiResourceInaccessible(str(errh))
        except requests.exceptions.RequestException as e:
            raise MediaWikiApiNetworkingException(str(e))
        except (KeyError, ValueError):
            # invalid json - a server-side problem
            raise MediaWikiApiResourceInaccessible("invalid response")
