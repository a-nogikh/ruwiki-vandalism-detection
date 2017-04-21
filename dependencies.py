from dotenv import load_dotenv, find_dotenv
from pymongo import MongoClient, collection
import geoip2.database
import maxminddb
from common.user_flags import UserFlags, UserFlagsTools
import os
from functools import lru_cache

load_dotenv(find_dotenv())


class DepRepo:

    @staticmethod
    @lru_cache(maxsize=2)
    def mongo_connection() -> MongoClient:
        mongo_connection = MongoClient('localhost', 27017)
        return mongo_connection

    @staticmethod
    @lru_cache(maxsize=2)
    def geoip() -> geoip2.database.Reader:
        geoip = geoip2.database.Reader(os.environ['GEO2_DIRECTORY'], maxminddb.MODE_MMAP_EXT)
        return geoip

    @staticmethod
    @lru_cache(maxsize=2)
    def flags() -> UserFlags:
        return UserFlagsTools.load('/home/alexander/user_groups.pkl')