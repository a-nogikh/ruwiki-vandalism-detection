from .mongodb.mongo_mapper import MongoMapper, MongoObjectMapper
from models import Instance, Page, Revision
from dependencies import injector
from injector import ClassAssistedBuilder
from typing import Generator


__all__ = ["InstanceCollection"]

class InstanceObjectMapper(MongoObjectMapper):

    # Short keys for mongo documents are intentional here.
    # Large datasets are expected, and this allows a more
    # compact representation 
    
    @staticmethod
    def from_dict(raw: dict) -> Instance:
        def get_page(page_raw: dict) -> Page:
            return Page(page_id=int(page_raw["id"]),
                        ns=int(page_raw["ns"]),
                        title=str(page_raw["title"])) 

        def get_revision(rev_raw: dict) -> Revision:
            return Revision(None,  # TODO
                            None,
                            comment=str(rev_raw["c"]))
        
        obj = Instance(revision_id=int(raw["rev_id"]),
                       page=get_page(raw["p"]))
        obj.feature_cache = raw.get("f", {})
        obj.revisions.replace([get_revision(x) for x in raw["r"]])

        return obj

    @staticmethod
    def to_dict(obj: Instance) -> dict:
        def convert_page(pg: Page) -> dict:
            return {
                "id": pg.page_id,
                "t": pg.title,
                "ns": pg.ns
            }

        def convert_rev(rv: Revision) -> dict:
            return {
                "id": rv.rev_id,
                "c": rv.comment
            }
        
        return {
            "rev_id": obj.revision_id,
            "p": convert_page(obj.page),
            "f": obj.feature_cache,
            "r": [convert_rev(x) for x in obj.revisions]
        }


class InstanceCollection:
    def __init__(self, name: str):
        builder = injector.get(ClassAssistedBuilder[MongoMapper])
        self.mapper = builder.build(collection_name=name,
                                    object_mapper=InstanceObjectMapper) # type: MongoMapper
    def query_all(self) -> Generator[Instance]:
        return self.mapper.query({})
        
    def insert(self, instance: Instance):
        self.mapper.insert(instance)

    def remove(self, instance: Instance):
        self.mapper.remove(instance)

    def save(self):
        self.mapper.save()

    def clear(self):
        self.mapper.clear()

    
    
