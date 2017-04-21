from collections import defaultdict
from dotenv import load_dotenv, find_dotenv
from pymongo import MongoClient, collection
from common.utils import bucket_items, parse_mw_date
from common.counter import Counter
import requests


load_dotenv(find_dotenv())

COLLECTION_NAME = 'any_train'

client = MongoClient('localhost', 27017)
raw_collection = client.wiki[COLLECTION_NAME]  # type: collection.Collection


# Generate sequence of required infos
def generate_raw(query):
    for page in query:
        revs = page["revs"]
        if len(revs) == 0:
            continue

        doc_id = page["_id"]
        last_rev = revs[-1]
        if last_rev["user"]["id"] is None:
            continue

        if "reg_date" not in last_rev["user"]:
            yield (last_rev["user"]["id"], (doc_id, "revs."+str(len(revs) - 1)+".user.reg_date"))


# Generate sequence of returned texts
def generate_answers(raw):
    for x in raw['query']['users']:
        if x is None or "registration" not in x:
            yield (x['userid'], None)
            continue

        if x["registration"] == "" or x["registration"] == None:
            yield (x['userid'], None)
            continue

        yield (x['userid'], parse_mw_date(x['registration']))


counter = Counter(100)
items = raw_collection.find({}, no_cursor_timeout=True)
for item in bucket_items(generate_raw(items), 50):
    ids = set()
    origin = defaultdict(list)
    for task in item:
        ids.add(task[0])
        origin[task[0]].append(task[1])

    str_ids = '|'.join(str(x) for x in ids)
    r = requests.get(
        'https://ru.wikipedia.org/w/api.php?format=json&action=query&list=users&usprop=registration&ususerids='
        + str_ids
    )
    '''with open('test.txt', 'w') as file:
        file.write(r.content.decode("utf-8"))
    print(r.content)
    exit(0)'''


    results = generate_answers(r.json())
    for x in results:
        for _origin in origin[x[0]]:
            raw_collection.update_one({
                "_id": _origin[0]
            }, {"$set": {
                _origin[1]: x[1]
            }})

        counter.tick()

counter.print()
