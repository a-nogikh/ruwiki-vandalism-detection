import pymongo
import copy


class _MongoObjectOperations:
    @staticmethod
    def get_diff(prev_dict: dict, curr_dict: dict):
        set_obj = {}
        unset_obj = {}
        
        def diff_recursive(prev, curr, prefix=""):
            nonlocal set_obj, unset_obj
            
            if type(prev) != type(curr):
                set_obj[prefix] = curr
                return

            base_prefix = prefix + "." if prefix != "" else ""
            if isinstance(prev, dict):
                for key, value in prev.items():
                    if key not in curr:
                        # the key must be removed
                        unset_obj[base_prefix + str(key)] = ""
                        continue
                    
                    diff_recursive(value, curr[key], base_prefix + str(key))

                # check new keys
                for key, value in curr.items():
                    if key in prev:
                        continue

                    set_obj[key] = value

            elif isinstance(prev, list):
                # tracking element adding/removal is not implemented 
                if len(prev) != len(curr):
                    set_obj[prefix] = curr
                else:
                    for key, value in enumerate(prev):
                        diff_recursive(value, curr[key], base_prefix + str(key))

            elif prev != curr:
                set_obj[prefix] = curr

                
        # run the recursion
        diff_recursive(prev_dict, curr_dict)
        
        result = {}
        if set_obj:
            result["$set"] = set_obj

        if unset_obj:
            result["$unset"] = unset_obj

        return result

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
        self.collection = database[collection_name]
        self.mapper = object_mapper
        self.db = database

        # variables for modifications accumulation
        self.id_to_object = dict()
        self.object_to_id = dict()
        self.id_to_copy = dict()
        self.to_insert = set()
        self.to_delete = set()
        
    def insert(self, obj):
        self.to_insert.insert(obj)
        self.to_delete.remove(obj)

    def remove(self, obj):
        self.to_delete.insert(obj)
        self.to_insert.remove(obj)

    def query(self, query_obj):
        return (self._convert_object(x) for x in self.collection.find(query_obj))

    def save(self):
        changes = []
        for obj in self.to_delete:
            if obj in self.id_to_object:
                changes.append(pymongo.DeleteOne({"_id": self.id_to_object[obj]}))
                self._forget_object(obj)

        for obj in self.to_insert:
            changes.append(pymongo.InsertOne(self.object_mapper.to_dict(obj)))

        for obj_id in self.id_to_object:
            mongo_diff = _MongoObjectOperations.get_diff(self.id_to_copy[obj_id],
                                                         self.id_to_object[obj_id])
            if mongo_diff:
                changes.append(pymongo.UpdateOne({'_id': obj_id}, mongo_diff))

        self.to_delete.clear()
        self.to_insert.clear()

        if changes:
            self.collection.bulk_write(changes)

    def clear(self):
        self.to_delete.clear()
        self.to_insert.clear()
        self.id_to_copy.clear()
        self.id_to_object.clear()
        self.object_to_id.clear()
        
    def _forget_object(self, obj):
        if obj in self.object_to_id:
            obj_id = self.object_to_id[obj]
            del self.id_to_copy[obj_id]
            del self.id_to_object[obj_id]
            del self.object_to_id[obj]
    
    def _convert_object(self, raw):
        obj_id = raw["_id"].str
        if obj_id in self.id_to_object:
            return self.id_to_object[obj_id]

        copied_obj = copy.deepcopy(raw)
        del copied_obj["_id"]

        mapped_obj = self.object_mapper.from_dict(copied_obj)
        self.id_to_object[obj_id] = mapped_obj
        self.id_to_copy[obj_id] = copied_obj
        self.object_to_id[mapped_obj] = obj_id

        return mapped_obj
