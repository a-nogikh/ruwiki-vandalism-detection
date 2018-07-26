import pymongo


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
