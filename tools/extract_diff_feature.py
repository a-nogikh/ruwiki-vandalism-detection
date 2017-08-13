from pymongo import MongoClient, collection
from common.counter import Counter
from features.feature import Feature
from text.parts_diff import PartsDiff
from common.utils import strip_accents, strip_blockquotes
from text.parts_extractor import PartsExtractor

COLLECTION_NAME = 'train_wcancel'

# TODO: take the later between reviewed and prev.user

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

    #if "rwords" in raw:
    #    cnt.tick()
    #    continue

    texts = Feature.revs(raw)

    if texts['prev_user'] is None or texts['current']['text'] is None:
        continue

    if texts['prev_user']['text'] is None:
        continue


    cnt.tick()
    #if cnt.value() < 18000:
   #      continue

    prev_text = strip_accents(texts['prev_user']['text']) #strip_blockquotes
    curr_text = strip_accents(texts['current']['text'])

    sentences_before = [x for x in extractor.extract_sentences(prev_text)]
    sentences_after = [x for x in extractor.extract_sentences(curr_text)]

    bigram_stemmed = PartsDiff.words_sum(
        extractor.extract_bigrams_stemmed(sentences_before),
        extractor.extract_bigrams_stemmed(sentences_after)
    )


    raw_collection.update_one({
        "_id": raw["_id"]
    }, {
        "$unset": {
            "bigram_stemmed": 1,
            "rwords": 1
        }
    })


    rwords = PartsDiff.words_sum(
        extractor.extract_wordnums(sentences_before),
        extractor.extract_wordnums(sentences_after)
    )

    raw_collection.update_one({
        "_id": raw["_id"]
    }, {
        "$set": {
            "bigram_stemmed": bigram_stemmed,
            "rwords": rwords
        }
    })


print ("Done")

