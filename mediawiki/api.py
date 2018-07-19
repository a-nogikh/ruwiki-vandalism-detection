import requests


class MediaWikiApi:
    def __init__(base_path: str):
        self.base_path = base_path

    def query_revisions_by_ids(self, page_ids: int, rvprop: list, rvlimit: int = 10):
        return self._get_query({
            "action": "query",
            "format": "json",
            "prop": "revisions",
            "revids": "|".join(page_ids),
            "rvprop": rvprop,
            "rvlimit": rvlimit
        })

    def _get_query(self, params: dict) -> dict:
        r = requests.get(self.base_path, params)
        # TODO: handle failure

        return r.json()
