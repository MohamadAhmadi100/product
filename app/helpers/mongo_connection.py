import pymongo

from app.config import settings


class Singleton(type):
    _instances = {}

    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super(Singleton, cls).__call__(*args, **kwargs)
        return cls._instances[cls]


class MongoConnection:
    client = None

    def __init__(self):
        self.client = pymongo.MongoClient(settings.MONGO_HOST, settings.MONGO_PORT,
                                          username=settings.MONGO_USER,
                                          password=settings.MONGO_PASS) if not self.client else self.client
        self.db = self.client['db-product']
        self.collection = self.db['product']
        self.product = self.db['new_product']
        self.archive = self.db['archive']
        self.kowsar_collection = self.db['kowsar']
        self.kowsar_config = self.db['kowsar_config']
        self.new_kowsar_collection = self.db['new_kowsar']
        self.parent_col = self.db['kowsar-parent']
        self.custom_category = self.db['custom-category']
        self.attributes_collection = self.db['attributes']
        self.master_server = pymongo.MongoClient(
            "200.100.100.220", 27017, username='root', password='qweasdQWEASD'
        )
        self.stocks_collection = self.master_server["msm"]["stocks"]
        self.warehouses_collection = self.master_server["msm"]["warehouse"]

        self.master_server = pymongo.MongoClient(
            "200.100.100.220", 27017, username='root', password='qweasdQWEASD'
        )
        self.warehouses_collection = self.master_server["msm"]["warehouse"]

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.client.close()
