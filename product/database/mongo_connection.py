import os
import sys

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
        print(os.getenv('MONGO_HOST'))
        self.client = pymongo.MongoClient(os.getenv("MONGO_HOST"), int(os.getenv("MONGO_PORT")), username=os.getenv("MONGO_USER"), password=os.getenv("MONGO_PASSWORD"))
        self.db = self.client['db-product']
        if 'pytest' in sys.modules:
            self.collection = self.db['test-products']
            self.kowsar_collection = self.db['test-kowsar']
        else:
            self.collection = self.db['products']
            self.kowsar_collection = self.db['kowsar']

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.client.close()
