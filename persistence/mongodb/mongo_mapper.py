from abc import ABC, abstractmethod

class MongoMapper(ABC):
    def __init__(self, collection_name: str):
        self.collection = collection_name

    def insert(obj):
        pass

    def query(query_obj):
        pass

    def save():
        pass

    @abstractmethod
    def _to_dict(obj):
        pass

    @abstractmethod
    def _from_dict(raw):
        pass
    
