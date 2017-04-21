from dotenv import load_dotenv, find_dotenv
from common.flagged_revs import FlaggedRevs, FlaggedTools
import os

load_dotenv(find_dotenv())

ORIG_FILE = '/media/sf_parts/total.txt'
uf = FlaggedRevs(ORIG_FILE)
FlaggedTools.save(uf, '/home/alexander/flagged.pkl')
