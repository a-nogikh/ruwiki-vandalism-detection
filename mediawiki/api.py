import requests
import typing
import logging
import itertools

logger = logging.getLogger(__name__)
logger.setLevel(logging.ERROR)
logging.basicConfig()


class MediaWikiApiResourceInaccessible(Exception):
    pass

class MediaWikiApiNetworkingException(MediaWikiApiResourceInaccessible):
    pass

class MediaWikiApi:
    def __init__(self, base_path: str):
        self.base_path = base_path


    def query_compare(self, from_rev: int, to_rev: int):
        return self._get_query({
            "format": "json",
            "action": "compare",
            "fromrev": from_rev,
            "torev": to_rev
        })["compare"]
        
    def query_revisions_for_page(self,
                                 page_id: int,
                                 rev_from: int,
                                 rvprop: list,
                                 revs_limit: int):
        query = {
            "action": "query",
            "format": "json",
            "prop": "revisions",
            "pageids": page_id,
            "rvdir": "older",
            "rvlimit": revs_limit,
            "rvprop": "|".join(str(x) for x in rvprop)
        }
        
        if rev_from is not None:
            query.update({ "rvstartid": rev_from })

        generator = self._get_all_query(query, "pages", str(page_id), "revisions")

        return itertools.islice(generator, revs_limit)

    def query_revisions_by_ids(self, rev_ids: int, rvprop: list):
        return self._get_all_query({
            "action": "query",
            "format": "json",
            "prop": "revisions",
            "revids": "|".join(str(x) for x in rev_ids),
            "rvprop": "|".join(str(x) for x in rvprop)
        }, "pages")

    def query_users_for_group(self, group_name: str):
        return self._get_all_query({
            "action": "query",
            "format": "json",
            "list": "allusers",
            "aulimit": 500,
            "augroup": group_name
        }, "allusers")

    def _get_all_query(self, params: dict, *fetch_key: str) -> typing.Iterator[dict]:
        query_params = params.copy()
        while True:
            response = self._get_query(query_params)
            query = response["query"]
            try:
                for x in fetch_key:
                    query = query[x]
            except:
                return # key not found
            
            if isinstance(query, dict):
                for key, x in query.items():
                    yield x
            elif isinstance(query, list):
                for x in query:
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
            params_debug = ' '.join([str(k) + "=" + str(v) for k,v in params.items()])
            logger.info("GET {}".format(params_debug))
            
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
