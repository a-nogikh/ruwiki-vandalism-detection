from pymongo import MongoClient, collection
from common.counter import Counter
from features.feature import Feature
from text.parts_diff import PartsDiff
from text.parts_extractor import PartsExtractor

COLLECTION_NAME = 'test_small'