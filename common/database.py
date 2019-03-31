

import pymongo


class Database(object):
    URI = "mongodb://jetfire:vivek95@ds043477.mlab.com:43477/heroku_hnv16g8k"
    DATABASE = None

    @staticmethod
    def initialize():
        client = pymongo.MongoClient(Database.URI)
        Database.DATABASE = client['heroku_hnv16g8k']

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