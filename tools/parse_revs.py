import datetime as dt
import gc
import os
import sys

import geoip2.database
import maxminddb
from dotenv import load_dotenv, find_dotenv
from pymongo import MongoClient

from common import utils
from common.page_processor import PageProcessor
from common.user_flags import UserFlagsTools
from flagged_revs import FlaggedTools
from mw.xml_dump import Iterator
from mw.xml_dump.functions import open_file

load_dotenv(find_dotenv())

file_name = sys.argv[1] if len(sys.argv) > 1 else os.environ['REVISION_SOURCE']
res = utils.query_yes_no("Revision source: " + file_name + "?", "no")
if not res:
    print("Exiting..")
    sys.exit()

#################
client = MongoClient('localhost', 27017)
db = client.wiki
geoip = geoip2.database.Reader(os.environ['GEO2_DIRECTORY'], maxminddb.MODE_MMAP_EXT)
flagged = FlaggedTools.load(os.environ['FLAGGED_REVISIONS'])
users = UserFlagsTools.load(os.environ['USER_FLAGS'])
#################


d1 = dt.datetime.now()
pp = PageProcessor(flagged, users, db, geoip)


cnt = 0; totalcnt = 0
rcnt = 0
#pr = cProfile.Profile()
#pr.enable()

dump = Iterator.from_file(open_file(file_name))

for page in dump:
    totalcnt += 1
    if totalcnt % 50 == 0:
        print(str(rcnt) + "/" + str(cnt) + "/" + str(totalcnt))
        gc.collect()

    excl = page.namespace != 0 and page.namespace != 10
    if not excl:
        cnt += 1
    # check page namespace
    rcnt+= pp.process(page, excl)
    if cnt >= 10:
        break

    page.clear()
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