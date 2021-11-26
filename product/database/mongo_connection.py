import os

import pymongo
from dotenv import load_dotenv


class Singleton(type):
    _instances = {}

    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super(Singleton, cls).__call__(*args, **kwargs)
        return cls._instances[cls]


class MongoConnection(metaclass=Singleton):
    def __init__(self):
        load_dotenv()
        self.client = pymongo.MongoClient(os.getenv("MONGO_HOST"), os.getenv("MONGO_PORT"))
        self.db = self.client['db-product']
        self.collection = self.db['products']
        self.kowsar_collection = self.db['kowsar']
        self.attribute_collection = self.db['attribute']

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.client.close()
