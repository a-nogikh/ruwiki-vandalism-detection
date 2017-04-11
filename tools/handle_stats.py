from collections import defaultdict
from dotenv import load_dotenv, find_dotenv
from pymongo import MongoClient, collection
from common.utils import bucket_items, parse_mw_date
from common.counter import Counter
import requests


load_dotenv(find_dotenv())

COLLECTION_NAME = 'stats'

client = MongoClient('localhost', 27017)
raw_collection = client.wiki[COLLECTION_NAME]  # type: collection.Collection

record = raw_collection.find_one()

guest_total =  sum([(sum(x["days_total"]) + sum(x["unknown_total"])) for x in record["guest"].values()])
guest_vandal =  sum([(sum(x["days_vandal"]) + sum(x["unknown_vandal"])) for x in record["guest"].values()])

users_total = sum(record["users"]["days_total"])
users_vandal = sum(record["users"]["days_vandal"])

users_weekprob = [record["users"]["days_vandal"][x]/record["users"]["days_total"][x] for  x in range(0, 7)]
guest_weekprob = [sum(x["days_vandal"][xx] for x in record["guest"].values())
                  /
                  sum(x["days_total"][xx] for x in record["guest"].values())

                  for  xx in range(0, 7)]

users_weekprob = [x/users_weekprob[0] for x in users_weekprob]
guest_weekprob = [x/guest_weekprob[0] for x in guest_weekprob]

print("guest: {}, user: {}".format(guest_vandal/guest_total, users_vandal/users_total))

print(record)
