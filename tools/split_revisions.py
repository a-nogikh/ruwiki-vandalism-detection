from random import random, seed

import pymongo
from dotenv import load_dotenv, find_dotenv
from pymongo import MongoClient, collection
from common.counter import Counter
from common.utils import query_yes_no

load_dotenv(find_dotenv())

if not query_yes_no("Do you really want to reset collections?"):
    exit()

TASK = {
    'test_small': {
        'vandal': 100,
        'good': 100
    },
    'train_small': {
        'vandal': 100,
        'good': 100
    }
}

client = MongoClient('localhost', 27017)

items_collection = client.wiki.items  # type: collection.Collection
total_count = 0

for collection_name in TASK:
    collection = client.wiki[collection_name]
    collection.delete_many({})
    collection.drop_indexes()
    collection.create_index([("r", pymongo.ASCENDING)])
    total_count += sum(TASK[collection_name].values())


# set random field
seed()
random_counter = Counter(100)
for item in items_collection.find({}, no_cursor_timeout=True):
    items_collection.update_one({'_id': item['_id']}, {
        '$set':{
                'r': random()
            }
        })
    random_counter.tick()

print("Random elements created")

# setting indices
indices = items_collection.index_information()
if 'random' not in indices:
    print("Creating index")
    items_collection.create_index([
            ("vandal", pymongo.ASCENDING),
            ("r", pymongo.ASCENDING)
        ],
        name="random")
    print("Index created")


vandal_items = items_collection.find({'vandal': True}, no_cursor_timeout=True).sort("r")
non_vandal_items = items_collection.find({'vandal': False}, no_cursor_timeout=True).sort("r")

# vandal

def split_generate(vandal_count, non_vandal_count):
    for _ in range(vandal_count):
        yield next(vandal_items)

    for _ in range(non_vandal_count):
        yield next(non_vandal_items)


print("Splitting items")
counter = Counter(100, total_count)
for collection_name, cnts in enumerate(TASK):
    collection = client.wiki[collection_name]
    for item in split_generate(cnts['vandal'], cnts['good']):
        item["r"] = random()
        del item["_id"]
        collection.insert_one(item)
        counter.tick()
