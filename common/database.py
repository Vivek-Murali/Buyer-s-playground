

import pymongo


class Database(object):
    URI = "mongodb://jetfire:vivek95@ds161410.mlab.com:61410/buyer"
    DATABASE = None

    @staticmethod
    def initialize():
        client = pymongo.MongoClient(Database.URI)
        Database.DATABASE = client['buyer']

    @staticmethod
    def insert(collection, data):
        Database.DATABASE[collection].insert(data)

    @staticmethod
    def find(collection, query):
        return Database.DATABASE[collection].find(query)

    @staticmethod
    def find_one(collection, query):
        return Database.DATABASE[collection].find_one(query)

    @staticmethod
    def initializing_City(collection, data):
        Database.DATABASE[collection].insert(data)

    @staticmethod
    def update(collection, query):
        return Database.DATABASE[collection].update_one(query)