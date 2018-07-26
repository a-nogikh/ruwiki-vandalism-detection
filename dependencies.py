from pymongo import MongoClient
from injector import Injector, provider

class InjectorModule:
    @provider
    def provide_database():
        client = MongoClient()
        return client["test_database"]
    

injector = Injector([InjectorModule])
