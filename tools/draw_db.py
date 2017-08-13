from dependencies import DepRepo
from common.plot_utils_small import draw_any

mongo = DepRepo.mongo_collection('stats_new')

rb = mongo.find_one({})["till_removed"]["rollback"]

y = rb["list"]#[0:144]
x = [i*5 for i,v  in enumerate(y)]
total = sum(y[:]) + rb["longer"]

print([
    total,
    y[0] / total,
    sum(y[0:6]) / total,
    sum(y[0:12]) / total,
    sum(y[0:(12*6)]) / total,
    sum(y[0:288]) / total,
])

#draw_any(x,y,"Minutes", "Edits","Sosi","test.png")
#print(sum(rb["list"][12:]))