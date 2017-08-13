from dependencies import DepRepo

reference_collection = DepRepo.mongo_collection('manual_dataset')
target_collection = DepRepo.mongo_collection('manual_new')

reference_values = dict()
for item in reference_collection.find({}):
    reference_values[item["revs"][-1]["id"]] = item["vandal"]


cnt = 0
for item in target_collection.find({}):
    last_id = item["revs"][-1]["id"]
    if last_id not in reference_values:
        continue

    if item["vandal"] != reference_values[last_id]:
       target_collection.update_one({"_id": item["_id"]}, {
           "$set":{
               "vandal": reference_values[last_id]
           }
       })

print (cnt)
