from app.helpers.mongo_connection import MongoConnection


class check_quantity:
    def __init__(self, product_object):
        self.system_code = product_object['systemCode']
        self.storage_id = product_object['storage_id']
        self.customer_type = product_object['customer_type']

    # def check_stocks(self):
    #     with MongoConnection() as client:
    #         msm_record = client.stocks_collection.find_one({"systemCode": self.system_code, "stockId": self.storage_id})
    #         if msm_record is None:
    #             return False
    #         else:
    #             return int(msm_record['quantity']) - int(msm_record['reserve'])

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
