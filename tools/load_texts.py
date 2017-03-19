from bson import ObjectId
from collections import defaultdict
from dotenv import load_dotenv, find_dotenv
from pymongo import MongoClient, collection
from common.utils import bucket_items
from common.counter import Counter
import requests

load_dotenv(find_dotenv())

COLLECTION_NAME = 'test_small'

client = MongoClient('localhost', 27017)
raw_collection = client.wiki[COLLECTION_NAME]  # type: collection.Collection


# Generate sequence of required texts
def generate_raw(query):
    for page in query:
        revs = page["revs"]
        if len(revs) == 0:
            continue

        doc_id = page["_id"]
        flagged_id = None
        if page['last_flagged'] is not None:
            if page['last_flagged']['text'] == '':
                yield (page['last_flagged']['id'], (doc_id, "last_flagged.text"))
                flagged_id = page['last_flagged']['id']

        rev_list = []
        prev = None
        for index, rev in enumerate(revs):
            if rev['id'] == page['session_start'] and prev is not None:
                if rev["text"] == "":
                    rev_list.append((prev['id'], index - 1))

            if rev['id'] == flagged_id or rev['id'] == page['last_trusted']:
                if rev["text"] == "":
                    rev_list.append((rev['id'], index))

            prev = rev

        if revs[-1]['text'] == "":
            rev_list.append((revs[-1]['id'], len(revs) - 1))

        for pair in set(rev_list):  # add unique
            yield (pair[0], (doc_id, "revs." + str(pair[1]) + ".text"))


# Generate sequence of returned texts
def generate_answers(raw):
    for x in raw['query']['pages'].items():
        for rev in x[1]['revisions']:
            yield (rev['revid'], rev['*'])


counter = Counter(100)
items = raw_collection.find({}, no_cursor_timeout=True)
for item in bucket_items(generate_raw(items), 100):
    ids = set()
    origin = defaultdict(list)
    for task in item:
        ids.add(task[0])
        origin[task[0]].append(task[1])

    str_ids = '|'.join(str(x) for x in ids)
    r = requests.get(
        'https://ru.wikipedia.org/w/api.php?action=query&format=json&prop=revisions&revids=' + str_ids + '&rvprop=content|ids')

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

# https://ru.wikipedia.org/w/api.php?action=query&prop=revisions&revids=1|2|3&rvprop=content|ids
