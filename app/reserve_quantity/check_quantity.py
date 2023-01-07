from app.helpers.mongo_connection import MongoConnection


class check_quantity:
    def __init__(self, product_object):
        self.system_code = product_object['systemCode']
        self.storage_id = product_object['storage_id']
        self.customer_type = product_object['customer_type']

    def check_quantity(self):
        with MongoConnection() as client:
            quantity = client.product.find_one({'system_code': self.system_code})
            if quantity is None:
                return False
            else:
                salable = quantity['warehouse_details'].get(self.customer_type)['storages'].get(self.storage_id)[
                              'quantity'] - \
                          quantity['warehouse_details'].get(self.customer_type)['storages'].get(self.storage_id)[
                              'reserved']
                return salable

    def check_price(self):
        with MongoConnection() as client:
            quantity = client.product.find_one({'system_code': self.system_code})
            if quantity is None:
                return False
            else:
                new_price = quantity['warehouse_details'].get(self.customer_type)['storages'].get(self.storage_id)[
                    'regular']
                return new_price
