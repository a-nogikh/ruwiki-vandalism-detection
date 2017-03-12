from mw.xml_dump import Iterator
from mw.xml_dump.functions import open_file
import datetime as dt
from page_processor import PageProcessor
from pymongo import MongoClient
from flagged_revs import FlaggedTools, FlaggedRevs
from user_flags import UserFlags, UserFlagsTools
import geoip2.database
import maxminddb
import os, gc
from dotenv import load_dotenv, find_dotenv
import statprof, cProfile, pstats, io

load_dotenv(find_dotenv())


#################
client = MongoClient('localhost', 27017)
db = client.wiki
geoip = geoip2.database.Reader(os.environ['GEO2_DIRECTORY'], maxminddb.MODE_MMAP_EXT)
flagged = FlaggedTools.load(os.environ['FLAGGED_REVISIONS'])
users = UserFlagsTools.load(os.environ['USER_FLAGS'])
#################


d1 = dt.datetime.now()
pp = PageProcessor(flagged, users, db, geoip)
pp.clear()

cnt = 0; totalcnt = 0
rcnt = 0
#pr = cProfile.Profile()
#pr.enable()
dump = Iterator.from_file(open_file(os.environ['REVISION_SOURCE']))
for page in dump:
    totalcnt += 1
    if totalcnt % 40 == 0:
        print(str(rcnt) + "/" + str(cnt) + "/" + str(totalcnt))
        gc.collect()

    #if page.namespace != 0 and page.namespace != 10: continue
    excl = page.namespace != 0 and page.namespace != 10
    if not excl:
        cnt += 1
    # check page namespace
    rcnt+= pp.process(page, excl)
    if cnt >= 500:
        break

    del page

pp.save()
d2 = dt.datetime.now()

print(d2-d1)
print (cnt)
print (rcnt)

'''
pr.disable()
s = io.StringIO()
sortby = 'cumulative'
ps = pstats.Stats(pr, stream=s).sort_stats(sortby)
ps.print_stats()
print(s.getvalue())
'''