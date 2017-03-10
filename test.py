from mw.xml_dump import Iterator
from mw.xml_dump.functions import open_file
import datetime as dt
from PageProcessor import PageProcessor
from pymongo import MongoClient, database
from FlaggedRevs import FlaggedTools, FlaggedRevs
from FlaggedUsers import FlaggedUsers
import geoip2.database
import maxminddb, collections, dotmap

import statprof, cProfile, pstats,io


#################
client = MongoClient('localhost', 27017)
db = client.wiki

assets = dotmap.DotMap()
assets.geoip = 'C:\\Users\\wp32p\\Desktop\\diploma\\data\\GeoLite2-City.mmdb'
assets.flagged_revs = 'C:\\Users\\wp32p\\Desktop\\diploma\\data\\flagged_list.pkl'
assets.rev_source = "C:\\Users\\wp32p\\Desktop\\diploma\\data\\part.gz"

geoip = geoip2.database.Reader(assets.geoip, maxminddb.MODE_MEMORY)

d1 = dt.datetime.now()

flagged = FlaggedTools.load(assets.flagged_revs)
pp = PageProcessor(flagged, FlaggedUsers(), db, geoip)
cnt = 0
rcnt = 0

dump = Iterator.from_file(open_file(assets.rev_source))

# Iterate through pages
for page in dump:
    if (page.namespace != 0): continue
    # check page namespace
    rcnt+=pp.process(page)
    cnt += 1
    if cnt >= 8:
        break

pp.save()
d2 = dt.datetime.now()

print((d2-d1))
print (cnt)
print (rcnt)

'''
pr = cProfile.Profile()
pr.disable()
s = io.StringIO()
sortby = 'cumulative'
ps = pstats.Stats(pr, stream=s).sort_stats(sortby)
ps.print_stats()
print(s.getvalue())
'''
#print(flagged.exists(82285068))

