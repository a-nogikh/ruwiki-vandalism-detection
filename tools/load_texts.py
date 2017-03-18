from dotenv import load_dotenv, find_dotenv
from pymongo import MongoClient

load_dotenv(find_dotenv())

client = MongoClient('localhost', 27017)
collection = client.wiki.items
# https://ru.wikipedia.org/w/api.php?action=query&prop=revisions&revids=1|2|3&rvprop=content|ids