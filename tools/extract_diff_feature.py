from pymongo import MongoClient, collection
from common.counter import Counter
from features.feature import Feature
from text.parts_diff import PartsDiff
from text.parts_extractor import PartsExtractor

COLLECTION_NAME = 'test_small'

client = MongoClient('localhost', 27017)
raw_collection = client.wiki[COLLECTION_NAME]  # type: collection.Collection

extractor = PartsExtractor()
for raw in raw_collection.find({}):
    if raw["revs"] is None or len(raw["revs"]) == 0:
        print(raw)  # this should not happen
        continue

    texts = Feature.revs(raw)
    sentences_before = extractor.extract_sentences(texts['prev_user']['text'])
    sentences_after = extractor.extract_sentences(texts['current']['text'])

    diff = PartsDiff.words_sum(
        extractor.extract_words_stemmed(sentences_before),
        extractor.extract_words_stemmed(sentences_after)
    )
    print(len(diff))