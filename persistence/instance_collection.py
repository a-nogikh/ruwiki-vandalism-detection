from .mongodb.mongo_mapper import MongoMapper
from models.instance import Instance


class InstanceCollection(MongoMapper):
    def __init__(self, name: str):
        super().__init__(name)
        
    def _from_dict(self, raw: dict) -> Instance:
        pass

    def _to_dict(self, obj: Instance) -> dict:
        pass
