from dependencies import DepRepo


COLLECTION_NAME_ORIG = 'new_items_wcancel'
COLLECTION_NAME_INTO = 'train_wcancel'
COUNT = 10000

source_collection = DepRepo.mongo_collection(COLLECTION_NAME_ORIG)
target_collection = DepRepo.mongo_collection(COLLECTION_NAME_INTO)

target_collection.delete_many({"vandal":False})

TRUSTED_GROUPS = ['editor', 'autoeditor', 'rollbacker', 'reviewer', 'sysop', 'bureaucrat']
users = DepRepo.flags()

existing_ids = set()
for item in DepRepo.mongo_collection('new_big_train').find({}):
    existing_ids.add(item["revs"][-1]["id"])


cnt = DepRepo.counter(100, COUNT)
excluded_ids = 0
for item in source_collection.find({'vandal': False}, no_cursor_timeout=True).sort("r"):
    if len(item["revs"]) < 2:
        continue

    last_rev = item["revs"][-1]
    if last_rev["user"]["id"] is not None:
        flags = users.get_flags(last_rev["user"]["id"])
        if flags is not None and any(1 for x in flags if x in TRUSTED_GROUPS):
            continue

    if item["revs"][-1]["id"] in existing_ids:
        excluded_ids += 1
        continue



    del item["_id"]
    target_collection.insert_one(item)
    cnt.tick()

    if cnt.value() > COUNT:
        break

print("Total skipped: {}".format(excluded_ids))
