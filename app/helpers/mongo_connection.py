from jdatetime import datetime
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
        self.log_db = self.client["db_log"]
        self.product = self.db['product']

        self.archive = self.db['archive']
        self.kowsar_collection = self.db['kowsar']
        self.custom_category = self.db['custom-category']
        self.attributes_collection = self.db['attributes']
        self.quantity_log = self.db['quantity_log']
        self.kowsar_log = self.db['kowsar_log']
        self.banners = self.db['banners']
        """
        reserves
        """
        self.warehouses = self.db['warehouse']
        self.imeis = self.db['imeis']
        self.product_archive = self.db['archive']
        self.cardex_collection = self.db['cardex']
        self.reserve_log_collection = self.db['reserve_log']

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.client.close()

    @property
    def log(self):
        week_of_month = (datetime.now().day - 1) // 7 + 1
        year_name = datetime.now().strftime("%Y-%m")
        return self.log_db[f"{year_name}-week-{week_of_month}"]
