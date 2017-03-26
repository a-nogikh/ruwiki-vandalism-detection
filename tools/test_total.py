from pymongo import MongoClient, collection


client = MongoClient('localhost', 27017)

raw_list = []
raw_res = []
for raw in client.wiki['train_small'] .find({}):
    if "tmp" not in raw or len(raw["tmp"]) == 0:
        continue

    if len(raw["revs"]) <= 1:
        continue

    raw_list.append(raw["f"])
    raw_res.append(1 if raw["vandal"] else 0)
