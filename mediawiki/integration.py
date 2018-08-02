from .api import MediaWikiApi
from models import Instance, Revision, Page, RegisteredUser, Guest


class MediaWikiObjectConversion:

    @staticmethod
    def convert_revision(raw: dict) -> Revision:
        if "anon" in raw:
            user = Guest(str(raw["user"]))
        else:
            user = RegisteredUser(int(raw["userid"]), str(raw["user"]))

        return Revision(str(raw["revid"]),
                        user,
                        None,
                        str(raw["comment"])) 

    @staticmethod
    def convert_page_only(raw: dict) -> Page:
        page = Page(page_id=int(raw["pageid"]),
                    title=str(raw["title"]),
                    ns=int(raw["ns"]))
                    
        return page

class BadRevisionIdException(Exception):
    pass

class MediaWikiIntegration:
    def __init__(self, api: MediaWikiApi):
        self.api = api

    def load_single_revision_instance(self, rev_id: int) -> Instance:
        attrs = ['ids', 'timestamp', 'user', 'userid', 'comment']
        response = self.api.query_revisions_by_ids([rev_id], attrs, 1)
        if "badrevids" in response:
            raise BadRevisionIdException()

        page_raw = next(response[x] for x in response.keys(), None)
        if page_raw is None:
            raise BadRevisionIdException()
            
        page = MediaWikiObjectConversion.convert_page_only(page_raw)

        instance = Instance(page, rev_id)
        instance.revisions.replace([
            MediaWikiObjectConversion.convert_revision(next(page_raw["revisions"]))
        ])

        return instance
