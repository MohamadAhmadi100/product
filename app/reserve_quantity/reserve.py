from app.helpers.mongo_connection import MongoConnection
from app.reserve_quantity.reserve_helper import add_reserve_quantity_order, add_reserve_msm_order, \
    dealership_add_reserve_quantity, dealership_add_reserve_msm, remove_from_quantity_cancel_order, \
    remove_from_msm_cancel_order, remove_quantity_edit_order, remove_msm_edit_order


class Reserve:
    def __init__(self, order):
        self.order: dict = order

    @property
    def order_data(self):
        provided_data = []
        customer_type = self.order["customer"]["type"]
        for item in self.order["splitedOrder"]:
            storage_id = item["storageId"]
            for product in item["products"]:
                product_detail = {
                    "system_code": product["systemCode"],
                    "storage_id": storage_id,
                    "count": product["count"],
                    "customer_type": customer_type,
                    "sku": product["name"],
                    "order_number": self.order['orderNumber']
                }
                provided_data.append(product_detail)
        return provided_data

    @staticmethod
    def add_to_reserve_order(system_code, storage_id, count, customer_type, sku, order_number):
        try:
            quantity_result = add_reserve_quantity_order(system_code, storage_id, count, customer_type, sku,
                                                         order_number)
            msm_result = add_reserve_msm_order(system_code, storage_id, count, order_number)
            if quantity_result.get("success") and msm_result.get("success"):
                with MongoConnection() as client:
                    client.stocks_collection.update_one(msm_result.get("query"), msm_result.get("update_data"))
                    client.product.replace_one(quantity_result.get("query"), quantity_result.get("replace_data"))
                return {"success": True, "message": "done", "status_code": 200,
                        "msm": msm_result.get("msm_cardex_data"),
                        "quantity": quantity_result.get("quantity_cardex_data")}
            else:
                return {"success": False, "error": f"{system_code}"}
        except TypeError:
            return {"success": False, "error": f"{system_code}"}
        except:
            return {"success": False, "error": f"{system_code}"}

    @staticmethod
    def add_to_reserve_dealership(system_code, storage_id, count, customer_type, sku, order_number):
        try:
            quantity_result = dealership_add_reserve_quantity(system_code, storage_id, count, customer_type, sku,
                                                              order_number)
            msm_result = dealership_add_reserve_msm(system_code, storage_id, count, order_number)
            if quantity_result.get("success") and msm_result.get("success"):
                with MongoConnection() as client:
                    client.stocks_collection.update_one(msm_result.get("query"), msm_result.get("update_data"))
                    client.product.replace_one(quantity_result.get("query"),
                                               quantity_result.get("replace_data"))
                return {"success": True, "message": "done", "status_code": 200,
                        "msm": msm_result.get("msm_cardex_data"),
                        "quantity": quantity_result.get("quantity_cardex_data")}
            else:
                return {"success": False, "error": f"{system_code}"}
        except TypeError:
            return {"success": False, "error": f"{system_code}"}
        except:
            return {"success": False, "error": f"{system_code}"}

    @staticmethod
    def remove_reserve_cancel(system_code, storage_id, count, customer_type, sku, order_number):
        try:
            quantity_result = remove_from_quantity_cancel_order(system_code, storage_id, count, customer_type, sku,
                                                                order_number)
            msm_result = remove_from_msm_cancel_order(system_code, storage_id, count, order_number)
            if quantity_result.get("success") and msm_result.get("success"):
                with MongoConnection() as client:
                    client.stocks_collection.update_one(msm_result.get("query"), msm_result.get("update_data"))
                    client.product.replace_one(quantity_result.get("query"),
                                               quantity_result.get("replace_data"))
                return {"success": True, "message": "done", "status_code": 200,
                        "msm": msm_result.get("msm_cardex_data"),
                        "quantity": quantity_result.get("quantity_cardex_data")}
        except TypeError:
            return {"success": False, "error": f"{system_code}"}
        except:
            return {"success": False, "error": f"{system_code}"}

    @staticmethod
    def cardex(user_id, user_name, order_number, cardex_details):
        with MongoConnection() as client:
            for item in cardex_details:
                cardex = {"userId": user_id, "userName": user_name, "orderNumber": order_number}
                cardex.update(item)
                client.cardex_collection.insert_one(cardex)
            return "cardex done"

    @staticmethod
    def msm_log(user_id, user_name, order_number, msm_details):
        with MongoConnection() as client:
            for item in msm_details:
                msm = {"userId": user_id, "userName": user_name, "orderNumber": order_number}
                msm.update(item)
                client.stocks_log_collection.insert_one(msm)
            return "msm done"

    @staticmethod
    def remove_reserve_edit_order(system_code, storage_id, count, customer_type, sku, order_number):
        try:
            quantity_result = remove_quantity_edit_order(system_code, storage_id, count, customer_type, sku,
                                                         order_number)
            msm_result = remove_msm_edit_order(system_code, storage_id, count, order_number)
            if quantity_result.get("success") and msm_result.get("success"):
                with MongoConnection() as client:
                    client.stocks_collection.update_one(msm_result.get("query"), msm_result.get("update_data"))
                    client.product.replace_one(quantity_result.get("query"), quantity_result.get("replace_data"))
                return {"success": True, "message": "done", "status_code": 200,
                        "msm": msm_result.get("msm_cardex_data"),
                        "quantity": quantity_result.get("quantity_cardex_data")}
        except TypeError:
            return {"success": False, "error": f"{system_code}"}
        except:
            return {"success": False, "error": f"{system_code}"}
