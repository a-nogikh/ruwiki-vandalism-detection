import logging
from injector import inject
from mediawiki import MediaWikiIntegration
from models import RegisteredUser
from persistence import GroupMembersCache


logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
logging.basicConfig()

class _UserGroupListsManager:
    @staticmethod
    def query_user_ids_set(group_name: str, api_integration: MediaWikiIntegration) -> set:
        res = set()
        for user in api_integration.load_group_members(group_name):
            res.add(user.user_id)

        return res
    
class UserGroupsFetcher:
    GROUPS_OF_INTEREST=('autoeditor', 'editor', 'bot')
    CACHE_TIME_SECONDS=3600*24

    @inject
    def __init__(self,
                 api_integration: MediaWikiIntegration,
                 cache: GroupMembersCache):
        self.api_integration = api_integration
        self.cache = cache

    def fetch_groups(self, user_id: int) -> list:
        user_groups = []
        for group in self.GROUPS_OF_INTEREST:
            if user_id in self._fetch_set_of_ids(group):
                user_groups.append(group)

        return user_groups

    def _fetch_set_of_ids(self, group_name: str) -> set:
        from_cache = self.cache.load_set(group_name)
        if from_cache is not None:
            return from_cache

        logger.info("fetching members of {} group from API".format(group_name))
        from_api = _UserGroupListsManager.query_user_ids_set(group_name, self.api_integration)
        logger.info("fetched {} members of {} group, saving".format(len(from_api),group_name))
        
        self.cache.save_set(group_name, from_api, self.CACHE_TIME_SECONDS)

        return from_api
