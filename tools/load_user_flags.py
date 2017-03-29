from dotenv import load_dotenv, find_dotenv
from common.user_flags import UserFlags, UserFlagsTools
import os

load_dotenv(find_dotenv())

ORIG_FILE = '/media/sf_parts/user_groups.json'
uf = UserFlags(ORIG_FILE)
UserFlagsTools.save(uf, '/home/alexander/user_groups.pkl')
