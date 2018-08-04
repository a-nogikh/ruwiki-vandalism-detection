from pymongo import MongoClient, database
from injector import Injector, Module, provider


class InjectorModule(Module):
    @provider
    def provide_database(self) -> database.Database:
        client = MongoClient()
        return client["test_database"]
    

injector = Injector([InjectorModule])
