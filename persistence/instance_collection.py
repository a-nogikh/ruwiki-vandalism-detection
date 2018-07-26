from .mongodb.mongo_mapper import MongoMapper, MongoObjectMapper
from models import Instance, Page
from dependencies import injector
from injector import ClassAssistedBuilder


__all__ = ["InstanceCollection"]

class InstanceObjectMapper(MongoObjectMapper):

    # Short keys for mongo documents are intentional here.
    # Large datasets are expected, and this may lead to a
    # more comact representation 
    
    @staticmethod
    def from_dict(raw: dict) -> Instance:
        def get_page(page_raw: dict) -> Page:
            return Page(page_id=int(page_raw["id"]),
                        ns=int(page_raw["ns"]),
                        title=str(page_raw["title"])) 
        
        obj = Instance(revision_id=int(raw["rev_id"]),
                       page=get_page(raw["p"]))
        obj.feature_cache = raw.get("f", {})

    @staticmethod
    def to_dict(obj: Instance) -> dict:
        def convert_page(pg: Page) -> dict:
            return {
                "id": pg.page_id,
                "t": pg.title,
                "ns": pg.ns
            }
        
        return {
            "rev_id": obj.revision_id,
            "p": convert_page(obj.page),
            "f": obj.feature_cache
        }


class InstanceCollection:
    def __init__(self, name: str):
        builder = injector.get(ClassAssistedBuilder[MongoMapper])
        self.mapper = builder.build(collection_name=name,
                                    object_mapper=InstanceObjectMapper) # type: MongoMapper

    def insert(self, instance: Instance):
        self.mapper.insert(instance)

    def remove(self, instance: Instance):
        self.mapper.remove(instance)

    def save(self):
        self.mapper.save()
    
