from collections import defaultdict
from dotenv import load_dotenv, find_dotenv
from pymongo import MongoClient, collection
from common.utils import bucket_items, parse_mw_date
from common.counter import Counter
import requests


load_dotenv(find_dotenv())

COLLECTION_NAME = 'train_wcancel'

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
        #if last_rev["user"]["id"] is not None:
        #    continue

        if "contrib_total" not in last_rev["user"]:
            yield (last_rev, (doc_id, "revs."+str(len(revs) - 1)+".user."))


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

print(len(list(generate_raw(raw_collection.find({}, no_cursor_timeout=True)))))

counter = Counter(50)
items = raw_collection.find({}, no_cursor_timeout=True)
for item in generate_raw(items):
    origin = defaultdict(list)

    r = requests.get(
        'https://ru.wikipedia.org/w/api.php?action=query&format=json&list=usercontribs&'+
        #'ucuserids='+ str(item[0]["user"]["id"])
        '&ucuser='+ str(item[0]["user"]["name"]) + "&ucstart=" +
        item[0]["timestamp"].strftime("%Y-%m-%dT%H:%M:%SZ") +
        "&ucprop=ids&uclimit=100"
    )

    total = 0
    pages = set()
    for x in r.json()["query"]["usercontribs"]:
        pages.add(x["pageid"])
        total += 1


    '''with open('test.txt', 'w') as file:
        file.write(r.content.decode("utf-8"))
    print(r.content)
    exit(0)'''

    print("{} : {} {}".format(str(item[0]["user"]["name"]), total, len(pages)))
    raw_collection.update_one({
        "_id": item[1][0]
    }, {"$set": {
        item[1][1]+"contrib_total": total,
        item[1][1] + "contrib_pages": len(pages),
    }})

    counter.tick()

counter.print()
