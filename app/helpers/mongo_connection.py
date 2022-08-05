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
        self.product = self.db['product']

        self.archive = self.db['archive']
        self.kowsar_collection = self.db['kowsar']
        self.kowsar_config = self.db['kowsar_config']
        self.parent_col = self.db['kowsar-parent']
        self.custom_category = self.db['custom-category']
        self.attributes_collection = self.db['attributes']
        """
        reserves
        """
        self.warehouses = self.db['warehouse']
        self.imeis = self.db['imeis']
        self.product_archive = self.db['archive']
        self.cardex_collection = self.db['cardex']
        self.reserve_log_collection = self.db['reserve_log']

        self.master_server = pymongo.MongoClient(
            "200.100.100.220", 27017, username='root', password='qweasdQWEASD'
        )
        self.stocks_collection = self.master_server["msm"]["stocks"]
        self.stocks_log_collection = self.master_server["msm"]["stock_logs"]
        self.warehouses_collection = self.master_server["msm"]["warehouse"]
        self.master_product_collection = self.master_server["warehouse"]["products"]

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.client.close()
