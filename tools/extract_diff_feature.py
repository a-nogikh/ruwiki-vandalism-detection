from pymongo import MongoClient, collection
from common.counter import Counter
from features.feature import Feature
from text.parts_diff import PartsDiff
from text.parts_extractor import PartsExtractor

COLLECTION_NAME = 'test_small'

client = MongoClient('localhost', 27017)
raw_collection = client.wiki[COLLECTION_NAME]  # type: collection.Collection

extractor = PartsExtractor()
cnt = Counter(50)

for raw in raw_collection.find({}):
    #if "tmp" in raw and raw["tmp"] is not None:
    #    continue

    if raw["revs"] is None or len(raw["revs"]) <= 1:
        #print(raw)   this should not happen
        continue

    texts = Feature.revs(raw)

    if texts['prev_user'] is None or texts['current']['text'] is None:
        continue

    sentences_before = extractor.extract_sentences(texts['prev_user']['text'])
    sentences_after = extractor.extract_sentences(texts['current']['text'])

    diff = PartsDiff.words_sum(
        extractor.extract_bigrams_stemmed(sentences_before),
        extractor.extract_bigrams_stemmed(sentences_after)
    )

    raw_collection.update_one({
        "_id": raw["_id"]
    }, {
        "$set": {
            "tmp": diff
        }
    })

    cnt.tick()

print ("Done")

