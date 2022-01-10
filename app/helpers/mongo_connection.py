import pymongo
from config import settings


class Singleton(type):
    _instances = {}

    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super(Singleton, cls).__call__(*args, **kwargs)
        return cls._instances[cls]


class MongoConnection(metaclass=Singleton):
    def __init__(self):
        self.client = pymongo.MongoClient(settings.MONGO_HOST, settings.MONGO_PORT,
                                          username=settings.MONGO_USER, password=settings.MONGO_PASS)
        self.db = self.client['db-product']
        self.collection = self.db['product']
        self.attribute_kowsar_collection = self.db['attr_kowsar']
        self.kowsar_collection = self.db['kowsar']

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.client.close()
