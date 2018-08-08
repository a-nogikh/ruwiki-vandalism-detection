from .mongodb.mongo_mapper import MongoMapper, MongoObjectMapper
from models import Instance, Page, Revision, User, Guest, RegisteredUser
from injector import ClassAssistedBuilder, inject
from typing import Iterator
import dateutil.parser


__all__ = ["InstanceCollection"]

class InstanceObjectMapper(MongoObjectMapper):

    # Short keys for mongo documents are intentional here.
    # Large datasets are expected, and this allows a more
    # compact representation 
    
    @staticmethod
    def from_dict(raw: dict) -> Instance:        
        obj = Instance(revision_id=int(raw["rev_id"]),
                       page=InstanceObjectMapper._page_from_dict(raw["p"]))
        obj.feature_cache = raw.get("f", {})
        obj.revisions.replace([InstanceObjectMapper._revision_from_dict(x) for x in raw["r"]])

        return obj

    @staticmethod
    def to_dict(obj: Instance) -> dict:
        return {
            "rev_id": int(obj.revision_id),
            "p": InstanceObjectMapper._page_to_dict(obj.page),
            "f": obj.feature_cache,
            "r": [InstanceObjectMapper._revision_to_dict(x) for x in obj.revisions]
        }

    # Private methods: page
    
    @staticmethod
    def _page_to_dict(pg: Page) -> dict:
        return {
            "id": int(pg.page_id),
            "t": pg.title,
            "ns": int(pg.ns)
        }

    @staticmethod
    def _page_from_dict(page_raw: dict) -> Page:
        return Page(page_id=int(page_raw["id"]),
                    ns=int(page_raw["ns"]),
                    title=str(page_raw["t"]))

    # Private methods: user
    
    @staticmethod
    def _user_to_dict(user) -> dict:
        if isinstance(user, Guest):
            return {
                "ip": user.ip
            }

        if isinstance(user, RegisteredUser):
            return {
                "id": int(user.user_id),
                "n": str(user.user_name)
            }
        
        return None
    
    @staticmethod
    def _user_from_dict(user_raw: dict) -> User:
        if "ip" in user_raw:
            return Guest(str(user_raw["ip"]))
        
        if "id" in user_raw:
            return RegisteredUser(int(user_raw["id"]), str(user_raw["n"]))

        return None

    # Private methods: revision
    
    @staticmethod
    def _revision_to_dict(rv: Revision) -> dict:
        return {
            "id": int(rv.rev_id),
            "c": rv.comment,
            "t": rv.timestamp.isoformat(),
            "u": InstanceObjectMapper._user_to_dict(rv.user),
            "is_m": rv.is_minor,
            "is_r": rv.is_reviewed
        }
    
    @staticmethod
    def _revision_from_dict(rev_raw: dict) -> Revision:
        return Revision(
            rev_id=int(rev_raw["id"]),
            user=InstanceObjectMapper._user_from_dict(rev_raw["u"]),  
            timestamp=dateutil.parser.parse(rev_raw["t"]),
            comment=str(rev_raw["c"]),
            is_minor=bool(rev_raw["is_m"]),
            is_reviewed=bool(rev_raw["is_r"])
        )


class InstanceCollection:
    @inject
    def __init__(self, name: str, builder: ClassAssistedBuilder[MongoMapper]):
        self.mapper = builder.build(collection_name=name,
                                    object_mapper=InstanceObjectMapper) # type: MongoMapper

    def query_all(self) -> Iterator[Instance]:
        return self.mapper.query({})
        
    def insert(self, instance: Instance):
        self.mapper.insert(instance)

    def remove(self, instance: Instance):
        self.mapper.remove(instance)

    def save(self):
        self.mapper.save()

    def clear(self):
        self.mapper.clear()

    
    
