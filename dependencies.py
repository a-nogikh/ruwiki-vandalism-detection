from redis import StrictRedis
from injector import Injector, Module, provider, singleton
from pymongo import MongoClient, database
from mediawiki import MediaWikiApi, MediaWikiIntegration
from persistence import GroupMembersCache
from services import UserGroupsFetcher


class MediaWikiModule(Module):
    @singleton
    @provider
    def provide_api(self) -> MediaWikiApi:
        return MediaWikiApi("https://ru.wikipedia.org/w/api.php")

    @singleton
    @provider
    def provide_mediawiki_integration(self, api: MediaWikiApi) -> MediaWikiIntegration:
        return MediaWikiIntegration(api)

    
class PersistenceModule(Module):
    @singleton
    @provider
    def provide_database(self) -> database.Database:
        client = MongoClient()
        return client["test_database"]

    @singleton
    @provider
    def provide_redis_client(self) -> StrictRedis:
        return StrictRedis(host='localhost', port=6379, db=0)
    
    @singleton
    @provider
    def provide_group_members_cache(self, redis_client: StrictRedis) -> GroupMembersCache:
        return GroupMembersCache(redis_client)

class ServicesModule(Module):
    @singleton
    @provider
    def provide_user_groups_fetcher(self,
                                    cache: GroupMembersCache,
                                    integration: MediaWikiIntegration) -> UserGroupsFetcher:
        return UserGroupsFetcher(integration, cache)

    
injector = Injector([MediaWikiModule, PersistenceModule, ServicesModule])
