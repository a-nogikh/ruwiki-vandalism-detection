import unittest
from persistence.mongodb.mongo_mapper import _MongoObjectOperations

class TestMongoMapper(unittest.TestCase):

    def test_diff_plain_equal(self):
        prev = {
            "a": 1,
            "b": "abc"
        }
        
        curr = {
            "a": 1,
            "b": "abc"
        }

        result = {}
        self.assertEqual(_MongoObjectOperations.get_diff(prev, curr), result)

    def test_diff_plain_not_equal(self):
        prev = {
            "a": 1,
            "b": "abc",
            "c": 123
        }
        
        curr = {
            "a": 2,
            "b": "abcd",
            "c": 123
        }

        result = {
            "$set": {
                "a": 2,
                "b": "abcd"
            }
        }
        self.assertEqual(_MongoObjectOperations.get_diff(prev, curr), result)

    def test_nested_dict_equal(self):
        prev = {
            "a": {
                "will_be_same": 1,
                "will_be_changed": "str"
            }
        }
        
        curr = {
            "a": {
                "will_be_same": 1,
                "will_be_changed": "new_str"
            }
        }

        result = {
            "$set": {
                "a.will_be_changed": "new_str"
            }
        }
        self.assertEqual(_MongoObjectOperations.get_diff(prev, curr), result)

    def test_diff_array_resize(self):
        prev = {
            "arr": [0,1,2,3],
            "will_be_changed": [0,1,2]
        }

        curr = {
            "arr": [0,1,2,3],
            "will_be_changed": [0,1,2,3]
        }

        # Current expected behaviour is to replace the whole array
        result = {
            "$set": {
                "will_be_changed":  [0,1,2,3]
            }
        }
        self.assertEqual(_MongoObjectOperations.get_diff(prev, curr), result)

    def test_diff_array_elements_update(self):
        prev = {
            "arr": [123, "string", { "key": "value" }],
        }

        curr = {
            "arr": [12345, "string", { "key": "new_value" }],
        }

        # Current expected behaviour is to replace the whole array
        result = {
            "$set": {
                "arr.0":  12345,
                "arr.2.key": "new_value"
            }
        }
        self.assertEqual(_MongoObjectOperations.get_diff(prev, curr), result)

    def test_diff_new_key(self):
        prev = {}
        
        curr = {
            "new_key": "new_value"
        }

        result = {
            "$set": {
                "new_key": "new_value"
            }
        }
        self.assertEqual(_MongoObjectOperations.get_diff(prev, curr), result)


    def test_diff_key_removal(self):
        prev = {
            "deleted_key": 123
        }
        
        curr = {}

        result = {
            "$unset": {
                "deleted_key": ""
            }
        }
        self.assertEqual(_MongoObjectOperations.get_diff(prev, curr), result)


    def test_diff_update_add_remove(self):
        prev = {
            "same": "Hello, world!",
            "changed": 0,
            "removed": {}
        }

        curr = {
            "same": "Hello, world!",
            "changed": 100,
            "added": "new string!"
        }

        result = {
            "$set": {
                "changed": 100,
                "added": "new string!"
            },
            "$unset": {
                "removed": ""
            }
        }

        self.assertEqual(_MongoObjectOperations.get_diff(prev, curr), result)


if __name__ == '__main__':
    unittest.main()
