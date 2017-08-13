from dependencies import DepRepo
from common.utils import assure_yes
from random import random
import pymongo

COLLECTION_NAME_ORIG = 'new_items_wcancel'
COLLECTION_NAME_INTO = 'train_wcancel'
COUNT = 10000

source_collection = DepRepo.mongo_collection(COLLECTION_NAME_ORIG)
target_collection = DepRepo.mongo_collection(COLLECTION_NAME_INTO)

assure_yes('Do you really want to put {} into {}?'.format(COLLECTION_NAME_ORIG, COLLECTION_NAME_INTO))
assure_yes('{} gonna be truncated'.format(COLLECTION_NAME_INTO))

target_collection.delete_many({})

existing_ids = set()
for item in DepRepo.mongo_collection('new_big_train').find({}):
    existing_ids.add(item["revs"][-1]["id"])


random_counter = DepRepo.counter(100)
print("Randomizing")
for item in source_collection.find({}, no_cursor_timeout=True):
    source_collection.update_one({'_id': item['_id']}, {
        '$set':{
                'r': random()
            }
        })
    random_counter.tick()

print("Random field created")

# setting indices
indices = source_collection.index_information()
if 'random' not in indices:
    print("Creating index")
    source_collection.create_index([
            ("vandal", pymongo.ASCENDING),
            ("r", pymongo.ASCENDING)
        ],
        name="random")
    print("Index created")

excluded_ids = 0
cnt = DepRepo.counter(100, COUNT)

for item in source_collection.find({'vandal': True}, no_cursor_timeout=True).sort("r"):
    if len(item["revs"]) < 2:
        continue

    if item["revs"][-1]["id"] in existing_ids:
        excluded_ids += 1
        continue

    del item["_id"]
    target_collection.insert_one(item)
    cnt.tick()

    if cnt.value() > COUNT:
        break

print("Total skipped: {}".format(excluded_ids))
