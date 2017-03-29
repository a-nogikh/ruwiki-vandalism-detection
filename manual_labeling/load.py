from pymongo import MongoClient, collection
import requests
from datetime import datetime
import os
from models.revision import Revision
from models.user import User
from dotenv import load_dotenv, find_dotenv
from common.user_flags import UserFlagsTools
from common.page_processor import PageProcessor
from common.rev_tools import RevTools
from common.counter import Counter
from common.utils import parse_mw_date

load_dotenv(find_dotenv())
users = UserFlagsTools.load(os.environ['USER_FLAGS'])

COLLECTION_NAME = 'labeled'

client = MongoClient('localhost', 27017)
db = client.wiki
db_coll = db[COLLECTION_NAME]  # type: collection.Collection


class TrustedUserException(Exception):
    pass


class SkippedException(Exception):
    pass


def load_revs(title, revid):
    url = 'https://ru.wikipedia.org/w/api.php?action=query&prop=revisions&rvstartid=' + revid \
          + '&rvprop=flags|timestamp|user|comment|ids|flagged|userid&titles=' + title \
          + '&rvlimit=50&format=json'
    res = requests.get(url)
    response = next(iter(res.json()["query"]["pages"].values()))  # type: dict

    raw_revs = response['revisions']
    if len(raw_revs) == 1:
        raise SkippedException()

    revs = [Revision(id=x['revid'],
                     timestamp=parse_mw_date(x['timestamp']), #datetime.strptime(x['timestamp']+" UTC", '%Y-%m-%dT%H:%M:%SZ %z'),
                     comment=x['comment'] if 'comment' in x else '',
                     minor='minor' in x,
                     flagged='flagged' in x,
                     text='',
                     user=User(
                         id=None if x['userid'] == 0 else x['userid'],
                         name=x['user'],
                         flags=users.get_flags(x['userid']) or []
                     )) for x in raw_revs]  # type: [Revision]
    revs.reverse()

    last_revision = revs[-1]  # type: Revision
    if 'bot' in last_revision.user.flags \
            or PageProcessor.is_trusted(last_revision.user.flags):
        raise TrustedUserException()

    last_trusted = None
    last_flagged = None
    for rev in reversed(revs):
        if last_trusted is None:
            if PageProcessor.is_trusted(rev.user.flags) or rev.flagged:
                last_trusted = rev

        if last_flagged is None:
            if rev.flagged:
                last_flagged = rev

    session_start = RevTools.session_start(revs)

    return {
        "page": {
            "id": response['pageid'],
            "title": title,
            "ns": response['ns']
        },
        'revs': [x.to_object() for x in revs],
        'last_trusted': None if last_trusted is None else last_trusted.id,
        'last_flagged': None if last_flagged is None else last_flagged.to_object(),
        'session_start': session_start.id
    }


cnt = Counter(50)
for item in db_coll.find({"info": None}, no_cursor_timeout=True):
    try:
        response = load_revs(item["q"]["title"], item["q"]["id"])
        db_coll.update_one({"_id": item["_id"]}, {"$set": {
            "info": response
        }})

        last_rev = response["revs"][-1]
        if last_rev['flagged']:
            db_coll.update_one({"_id": item["_id"]}, {"$set": {
                "is_auto": True,
                "status": 1
            }})

    except SkippedException:
        db_coll.update_one({"_id": item["_id"]}, {"$set": {
            "is_skipped": True
        }})

    except TrustedUserException:
        db_coll.update_one({"_id": item["_id"]}, {"$set": {
            "is_trusted": True
        }})

    cnt.tick()
