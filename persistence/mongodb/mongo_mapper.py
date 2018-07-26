import pymongo


class _MongoObjectOperations:
    def get_diff(prev_dict, curr_dict):
        pass

class MongoObjectMapper:
    @staticmethod
    def to_dict(obj):
        pass

    @staticmethod
    def from_dict(obj):
        pass

# Data mapper & unit of work approach
class MongoMapper:
    def __init__(self,
                 collection_name: str,
                 database: pymongo.database.Database,
                 object_mapper: MongoObjectMapper):
        self.collection = collection_name
        self.mapper = object_mapper
        self.db = database

        # variables for modifications accumulation
        self.object_map = dict()
        self.to_insert = set()
        self.to_delete = set()
        
    def insert(self, obj):
        self.to_insert.insert(obj)
        self.to_delete.remove(obj)

    def remove(self, obj):
        self.to_delete.insert(obj)
        self.to_insert.remove(obj)

    def query(self, query_obj):
        pass

    def save(self):
        pass
