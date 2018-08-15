from dateutil import parser
from injector import inject, ClassAssistedBuilder
from typing import Iterator
from .mongodb.mongo_mapper import MongoMapper, MongoObjectMapper
from models import LabelingTask

__all__ = ["LabelingTaskCollection"]

class LabelingTaskObjectMapper(MongoObjectMapper):    
    @staticmethod
    def from_dict(raw: dict) -> LabelingTask:
        return LabelingTask(
            rev_from=int(raw["rev_from"]),
            rev_to=int(raw["rev_to"]),
            tags=[str(x) for x in raw["tags"]],
            labeled_at=parser.parse(raw["labeled_at"]) if raw["labeled_at"] is not None else None,
            cached_diff=raw["cached_diff"],
            cached_title=raw["cached_title"],
            cached_username=raw["cached_username"])

    @staticmethod
    def to_dict(obj: LabelingTask) -> dict:
        return {
            "rev_from": int(obj.rev_from),
            "rev_to": int(obj.rev_to),
            "tags": obj.tags,
            "labeled_at": obj.labeled_at.isoformat() if obj.labeled_at is not None else None,
            "cached_diff": obj.cached_diff,
            "cached_title": obj.cached_title,
            "cached_username": obj.cached_username
        }

class LabelingTaskCollection:
    @inject
    def __init__(self, builder: ClassAssistedBuilder[MongoMapper]):
        self.mapper = builder.build(collection_name="labeling_tasks",
                                    object_mapper=LabelingTaskObjectMapper) # type: MongoMapper

    def query_all(self) -> Iterator[LabelingTask]:
        return self.mapper.query({})
        
    def insert(self, instance: LabelingTask):
        self.mapper.insert(instance)

    def remove(self, instance: LabelingTask):
        self.mapper.remove(instance)

    def save(self):
        self.mapper.save()

    def clear(self):
        self.mapper.clear()
    
