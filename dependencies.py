from dotenv import load_dotenv, find_dotenv
from pymongo import MongoClient, collection
import geoip2.database
import maxminddb
import os

load_dotenv(find_dotenv())


class DepRepo:

    @staticmethod
    @property
    def mongo_connection() -> MongoClient:
        mongo_connection = MongoClient('localhost', 27017)
        return mongo_connection

    @staticmethod
    @property
    def geoip() -> geoip2.database.Reader:
        geoip = geoip2.database.Reader(os.environ['GEO2_DIRECTORY'], maxminddb.MODE_MMAP_EXT)
        return geoip
