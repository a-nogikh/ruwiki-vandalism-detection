import requests
import typing


class MediaWikiApiResourceInaccessible(Exception):
    pass

class MediaWikiApiNetworkingException(MediaWikiApiResourceInaccessible):
    pass

class MediaWikiApi:
    def __init__(self, base_path: str):
        self.base_path = base_path

    def query_revisions_by_ids(self, page_ids: int, rvprop: list):
        return self._get_all_query({
            "action": "query",
            "format": "json",
            "prop": "revisions",
            "revids": "|".join(str(x) for x in page_ids),
            "rvprop": "|".join(str(x) for x in rvprop)
        }, "pages")

    def query_users_for_group(self, group_name: str):
        return self._get_all_query({
            "action": "query",
            "format": "json",
            "list": "allusers",
            "aulimit": 500
        }, "allusers")
    
    def _get_all_query(self, params: dict, fetch_key: str) -> typing.Iterator[dict]:
        query_params = params.copy()
        while True:
            response = self._get_query(query_params)
            query = response["query"]
            if fetch_key not in query:
                return
            
            for key, x in query[fetch_key].items():
                yield x
            
            if "continue" in response:
                for key in response["continue"]:
                    if key != "continue":
                        query_params[key] = response["continue"][key]
            else:
                # We have queried everything
                break
                

    def _get_query(self, params: dict) -> dict:
        try:
            r = requests.get(self.base_path, params)
            r.raise_for_status()
            
            return r.json()
        except requests.exceptions.HTTPError as errh:
            raise MediaWikiApiResourceInaccessible(str(errh))
        except requests.exceptions.RequestException as e:
            raise MediaWikiApiNetworkingException(str(e))
        except (KeyError, ValueError):
            # invalid json - a server-side problem
            raise MediaWikiApiResourceInaccessible("invalid response")
