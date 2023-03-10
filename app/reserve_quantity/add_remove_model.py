import jdatetime

from app.helpers.mongo_connection import MongoConnection
from app.helpers.warehouses import find_warehouse


class AddRemoveQtyReserve:
    def __init__(self):
        self.cardex = {}

    def add_reserve(self, system_code, storage_id, count, customer_type, order_number):
        """
        add reserve to product
        """
        with MongoConnection() as client:
            quantity_count = client.product.count_documents({"system_code": system_code})
            if quantity_count > 0:
                product = client.product.find({"system_code": system_code}, {"_id": False})
                for products in product:
                    for cusrsor, storage_dict in products['warehouse_details'].get(customer_type)['storages'].items():
                        if cusrsor == storage_id:
                            if (storage_dict["reserved"] + count) <= storage_dict['quantity']:
                                self.cardex['name'] = products['name']
                                self.cardex['qty'] = count
                                self.cardex['oldReserve'] = storage_dict["reserved"]
                                storage_dict["reserved"] += count
                                self.cardex['newReserve'] = storage_dict["reserved"]
                                self.cardex['oldQuantity'] = storage_dict["quantity"]
                                self.cardex['oldInventory'] = storage_dict["inventory"]
                                self.cardex['newQuantity'] = storage_dict["quantity"]
                                self.cardex['newInventory'] = storage_dict["inventory"]
                                self.cardex['customerType'] = customer_type
                                client.product.replace_one({"system_code": system_code}, products)
                                return {"success": True, "cardex": self.cardex}
                            else:
                                client.reserve_log_collection.insert_one(
                                    {"systemCode": str(system_code), "stockId": str(storage_id),
                                     "old_reserve": storage_dict["reserved"],
                                     "new_reserve": storage_dict["reserved"] + count,
                                     "old_qty": storage_dict["quantity"],
                                     "new_qty": storage_dict["quantity"],
                                     "count": count,
                                     "order_number": order_number, "message": "reserve bishtar az quantity",
                                     "edit_date": str(jdatetime.datetime.now()).split(".")[0]})
                                return {"success": False, "status_code": 400}

    def remove_reserve(self, system_code, storage_id, count, customer_type, order_number):
        """
        remove reserve from product
        """
        with MongoConnection() as client:
            quantity_count = client.product.count_documents({"system_code": system_code})
            if quantity_count > 0:
                product = client.product.find({"system_code": system_code}, {"_id": False})
                for products in product:
                    for cusrsor, storage_dict in products['warehouse_details'].get(customer_type)['storages'].items():
                        if cusrsor == storage_id:
                            if (storage_dict["reserved"] - count) >= 0:
                                self.cardex['name'] = products['name']
                                self.cardex['qty'] = count
                                self.cardex['oldReserve'] = storage_dict["reserved"]
                                storage_dict["reserved"] -= count
                                self.cardex['newReserve'] = storage_dict["reserved"]
                                self.cardex['oldQuantity'] = storage_dict["quantity"]
                                self.cardex['newQuantity'] = storage_dict["quantity"]
                                self.cardex['customerType'] = customer_type
                                client.product.replace_one({"system_code": system_code}, products)
                                return {"success": True, "cardex": self.cardex}
                            else:
                                client.reserve_log_collection.insert_one(
                                    {"systemCode": str(system_code), "stockId": str(storage_id),
                                     "old_reserve": storage_dict["reserved"],
                                     "new_reserve": storage_dict["reserved"] - count,
                                     "old_qty": storage_dict["quantity"],
                                     "new_qty": storage_dict["quantity"],
                                     "count": count,
                                     "order_number": order_number, "message": "reserve manfi",
                                     "edit_date": str(jdatetime.datetime.now()).split(".")[0]})
                                return {"success": False, "error": "???????????? ???? ???????? ???????? ????????", "status_code": 400}

    def add_quantity(self, system_code, storage_id, count, customer_type, price):
        """
        add quantity to product
        """
        with MongoConnection() as client:
            quantity_count = client.product.count_documents({"system_code": system_code})
            if quantity_count > 0:
                product = client.product.find({"system_code": system_code}, {"_id": False})
                for products in product:
                    self.cardex['name'] = products['name']
                    found_storage = False
                    for cusrsor, storage_dict in products['warehouse_details'].get(customer_type)['storages'].items():
                        if cusrsor == storage_id and storage_dict.get("quantity") is not None and storage_dict.get(
                                "reserved") is not None:
                            found_storage = True
                            break
                    if found_storage:
                        for cusrsor, storage_dict in products['warehouse_details'].get(customer_type)[
                            'storages'].items():
                            if cusrsor == storage_id:
                                if storage_dict.get("inventory") is None:
                                    storage_dict["inventory"] = count
                                else:
                                    storage_dict["inventory"] += count
                                self.cardex['qty'] = count
                                self.cardex['oldQuantity'] = storage_dict["quantity"]
                                self.cardex['oldInventory'] = storage_dict["inventory"]
                                storage_dict["quantity"] += count
                                self.cardex['newQuantity'] = storage_dict["quantity"]
                                self.cardex['newInventory'] = storage_dict["inventory"]
                                self.cardex['oldReserve'] = storage_dict["reserved"]
                                self.cardex['newReserve'] = storage_dict["reserved"]
                                self.cardex['customerType'] = customer_type
                                if price is not None:
                                    storage_dict["regular"] = price
                                client.product.update_one({"system_code": system_code}, {"$set": products})
                                return {"success": True, "cardex": self.cardex}
                    else:
                        self.cardex['qty'] = count
                        self.cardex['oldQuantity'] = 0
                        self.cardex['oldInventory'] = 0
                        self.cardex['newQuantity'] = count
                        self.cardex['newInventory'] = count
                        self.cardex['oldReserve'] = 0
                        self.cardex['newReserve'] = 0
                        self.cardex['customerType'] = customer_type
                        warehouse_detail = find_warehouse(storage_id)
                        client.product.update_one(
                            {"system_code": system_code},
                            {"$set": {f"warehouse_details.{customer_type}.storages.{storage_id}": {
                                "storage_id": storage_id,
                                "regular": price,
                                "reserved": 0,
                                "quantity": count,
                                "inventory": count,
                                "min_qty": 1,
                                "max_qty": 1,
                                "warehouse_state": warehouse_detail['warehouses'].get('state'),
                                "warehouse_city": warehouse_detail['warehouses'].get('city'),
                                "warehouse_state_id": str(warehouse_detail['warehouses'].get('state_id')),
                                "warehouse_city_id": warehouse_detail['warehouses'].get('city_id'),
                                "warehouse_label": warehouse_detail['warehouses'].get('warehouse_name')
                            }
                            }})
                        return {"success": True, "cardex": self.cardex}
            else:
                client.reserve_log_collection.insert_one(
                    {"systemCode": str(system_code), "stockId": str(storage_id),
                     "message": "product not found in add qty",
                     "edit_date": str(jdatetime.datetime.now()).split(".")[0]})
                return {"success": False, "error": "?????????? ???? ???????? ?????? ???? ?????????????? ?????????????? ???????? ??????????",
                        "status_code": 404}

    def remove_reserve_quantity(self, system_code, storage_id, count, customer_type):
        """
        remove quantity and reserve from product
        """
        with MongoConnection() as client:
            quantity_count = client.product.count_documents({"system_code": system_code})
            if quantity_count > 0:
                product = client.product.find({"system_code": system_code}, {"_id": False})
                for products in product:
                    for cusrsor, storage_dict in products['warehouse_details'].get(customer_type)['storages'].items():
                        if cusrsor == storage_id:
                            if storage_dict["quantity"] > 0 or storage_dict["reserved"] > 0:
                                self.cardex['qty'] = count
                                self.cardex['oldQuantity'] = storage_dict["quantity"]
                                self.cardex['oldInventory'] = storage_dict["inventory"]
                                storage_dict["quantity"] -= count
                                storage_dict["inventory"] -= count
                                self.cardex['newQuantity'] = storage_dict["quantity"]
                                self.cardex['newInventory'] = storage_dict["inventory"]
                                self.cardex['oldReserve'] = storage_dict["reserved"]
                                storage_dict["reserved"] -= count
                                self.cardex['newReserve'] = storage_dict["reserved"]
                                self.cardex['customerType'] = customer_type
                                if storage_dict["quantity"] < 0 or storage_dict["reserved"] < 0:
                                    return {"success": False, "error": "?????????? ???? ???????????? ?????????? ?????? ???? ?????????? ???????? ???????? ??????",
                                            "status_code": 404}
                                client.product.update_one({"system_code": system_code}, {"$set": products})
                                return {"success": True, "cardex": self.cardex}
                            else:
                                client.reserve_log_collection.insert_one(
                                    {"systemCode": str(system_code), "stockId": str(storage_id),
                                     "message": "reserve or qty kamtar az 0",
                                     "edit_date": str(jdatetime.datetime.now()).split(".")[0]})
                                return {"success": False, "error": "???????????? ???? ???????? ???????? ???? ?????????????? ??????",
                                        "status_code": 404}
            else:
                client.reserve_log_collection.insert_one(
                    {"systemCode": str(system_code), "stockId": str(storage_id),
                     "message": "product not found in remove qty",
                     "edit_date": str(jdatetime.datetime.now()).split(".")[0]})
                return {"success": False, "error": "?????????? ???? ???????? ?????? ???????? ??????????", "status_code": 404}

    def add_quantity_dealership(self, system_code, storage_id, count, customer_type):
        """
        add quantity to product
        """
        with MongoConnection() as client:
            quantity_count = client.product.count_documents({"system_code": system_code})
            if quantity_count > 0:
                product = client.product.find({"system_code": system_code}, {"_id": False})
                for products in product:
                    self.cardex['name'] = products['name']
                    found_storage = False
                    for cusrsor, storage_dict in products['warehouse_details'].get(customer_type)['storages'].items():
                        if cusrsor == storage_id:
                            found_storage = True
                    if found_storage:
                        for cusrsor, storage_dict in products['warehouse_details'].get(customer_type)[
                            'storages'].items():
                            if cusrsor == storage_id:
                                self.cardex['qty'] = count
                                self.cardex['oldQuantity'] = storage_dict["quantity"]
                                self.cardex['oldInventory'] = storage_dict["inventory"]
                                storage_dict["quantity"] += count
                                storage_dict["inventory"] += count
                                self.cardex['newQuantity'] = storage_dict["quantity"]
                                self.cardex['newInventory'] = storage_dict["inventory"]
                                self.cardex['oldReserve'] = storage_dict["reserved"]
                                self.cardex['newReserve'] = storage_dict["reserved"]
                                self.cardex['customerType'] = customer_type
                                client.product.update_one({"system_code": system_code}, {"$set": products})
                                return {"success": True, "cardex": self.cardex}
                    else:
                        self.cardex['qty'] = count
                        self.cardex['oldQuantity'] = 0
                        self.cardex['oldInventory'] = 0
                        self.cardex['newQuantity'] = count
                        self.cardex['newInventory'] = count
                        self.cardex['oldReserve'] = 0
                        self.cardex['newReserve'] = 0
                        self.cardex['customerType'] = customer_type
                        warehouse_detail = find_warehouse(storage_id)
                        client.product.update_one(
                            {"system_code": system_code},
                            {"$set": {f"warehouse_details.{customer_type}.storages.{storage_id}": {
                                "storage_id": storage_id,
                                "regular": 0,
                                "reserved": 0,
                                "quantity": count,
                                "inventory": count,
                                "min_qty": 1,
                                "max_qty": 1,
                                "warehouse_state": warehouse_detail['warehouses'].get('state'),
                                "warehouse_city": warehouse_detail['warehouses'].get('city'),
                                "warehouse_state_id": str(warehouse_detail['warehouses'].get('state_id')),
                                "warehouse_city_id": warehouse_detail['warehouses'].get('city_id'),
                                "warehouse_label": warehouse_detail['warehouses'].get('warehouse_name')
                            }
                            }})
                        return {"success": True, "cardex": self.cardex}
            else:
                client.reserve_log_collection.insert_one(
                    {"systemCode": str(system_code), "stockId": str(storage_id),
                     "message": "product not found in add qty",
                     "edit_date": str(jdatetime.datetime.now()).split(".")[0]})
                return {"success": False, "error": "?????????? ???? ???????? ?????? ???? ?????????????? ?????????????? ???????? ??????????",
                        "status_code": 404}
