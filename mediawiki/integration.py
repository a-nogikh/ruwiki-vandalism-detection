import dateutil.parser
from injector import inject
from .api import MediaWikiApi
from models import Instance, Revision, Page, RegisteredUser, Guest


class MediaWikiObjectConversion:

    @staticmethod
    def convert_revision(raw: dict) -> Revision:
        if "anon" in raw:
            user = Guest(str(raw["user"]))
        else:
            user = RegisteredUser(int(raw["userid"]), str(raw["user"]))

        return Revision(rev_id=int(raw["revid"]),
                        user=user,
                        timestamp=dateutil.parser.parse(raw["timestamp"]),
                        comment=str(raw["comment"]),
                        is_minor=("minor" in raw)) 

    @staticmethod
    def convert_page(raw: dict) -> Page:
        page = Page(page_id=int(raw["pageid"]),
                    title=str(raw["title"]),
                    ns=int(raw["ns"]))
                    
        return page

class BadRevisionIdException(Exception):
    pass

class MediaWikiIntegration:
    @inject
    def __init__(self, api: MediaWikiApi):
        self.api = api

    def load_single_revision_instance(self, rev_id: int) -> Instance:
        attrs = ['ids', 'timestamp', 'user', 'userid', 'comment', 'flags']
        response = self.api.query_revisions_by_ids([rev_id], attrs)
        if "badrevids" in response:
            raise BadRevisionIdException()

        page_raw = next((response["pages"][x] for x in response["pages"].keys()), None)
        if page_raw is None:
            raise BadRevisionIdException()
            
        page = MediaWikiObjectConversion.convert_page(page_raw)

        instance = Instance(page, rev_id)
        instance.revisions.replace([
            MediaWikiObjectConversion.convert_revision(page_raw["revisions"][0])
        ])

        return instance
