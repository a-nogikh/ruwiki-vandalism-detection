from mediawiki import MediaWikiApi
from pymongo import MongoClient, database
from injector import Injector, Module, provider, singleton


class InjectorModule(Module):
    @singleton
    @provider
    def provide_api(self) -> MediaWikiApi:
        return MediaWikiApi("https://ru.wikipedia.org/w/api.php")
    
    @singleton
    @provider
    def provide_database(self) -> database.Database:
        client = MongoClient()
        return client["test_database"]
    

injector = Injector([InjectorModule])
