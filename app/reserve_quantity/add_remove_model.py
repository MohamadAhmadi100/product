import jdatetime

from app.helpers.mongo_connection import MongoConnection
from app.helpers.warehouses import find_warehouse


class AddRemoveReserve:
    @staticmethod
    def add_reserve_quantity(system_code, storage_id, count, customer_type, order_number):
        with MongoConnection() as client:
            quantity_count = client.product.count_documents({"system_code": system_code})
            if quantity_count > 0:
                product = client.product.find({"system_code": system_code}, {"_id": False})
                for products in product:
                    for cusrsor, storage_dict in products['warehouse_details'].get(customer_type)['storages'].items():
                        if cusrsor == storage_id:
                            if (storage_dict["reserved"] + count) <= storage_dict['quantity']:
                                storage_dict["reserved"] += count
                                return {"success": True,
                                        "query": {"system_code": system_code},
                                        "replace_data": products,
                                        "storage_data": storage_dict}
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
                                return {"success": False}

    @staticmethod
    def add_reserve_msm(system_code, storage_id, count, order_number):
        with MongoConnection() as client:
            try:
                product_count = client.stocks_collection.count_documents(
                    {"systemCode": str(system_code), "stockId": str(storage_id)})

                if product_count > 0:
                    product = client.stocks_collection.find_one(
                        {"systemCode": str(system_code), "stockId": str(storage_id)},
                        {"_id": False})

                    if (int(product["reserve"]) + count) <= int(product["quantity"]):
                        update_data = {"$set": {"reserve": int(product["reserve"]) + count}}
                        query_data = {"systemCode": str(product["systemCode"]), "stockId": str(product["stockId"])}

                        return {"success": True, "query": query_data, "product": product,
                                "update_data": update_data}

                    else:
                        client.reserve_log_collection.insert_one(
                            {"systemCode": str(system_code), "stockId": str(storage_id), "orderNumber": order_number,
                             "message": "reserve bishtar az quantity",
                             "editDate": str(jdatetime.datetime.now()).split(".")[0]})
                        return {"success": False}

                else:
                    client.reserve_log_collection.insert_one(
                        {"systemCode": str(system_code), "stockId": str(storage_id), "orderNumber": order_number,
                         "message": "system code not found!", "editDate": str(jdatetime.datetime.now()).split(".")[0]})
                    return {"success": False}

            except:
                client.reserve_log_collection.insert_one(
                    {"systemCode": str(system_code), "stockId": str(storage_id), "orderNumber": order_number,
                     "message": "root exception", "editDate": str(jdatetime.datetime.now()).split(".")[0]})
                return {"success": False}

    @staticmethod
    def remove_reserve_quantity(system_code, storage_id, count, customer_type, order_number):
        with MongoConnection() as client:
            quantity_count = client.product.count_documents({"system_code": system_code})
            if quantity_count > 0:
                product = client.product.find({"system_code": system_code}, {"_id": False})
                for products in product:
                    for cusrsor, storage_dict in products['warehouse_details'].get(customer_type)['storages'].items():
                        if cusrsor == storage_id:
                            if (storage_dict["reserved"] - count) >= 0:
                                storage_dict["reserved"] -= count
                                return {"success": True,
                                        "query": {"system_code": system_code},
                                        "replace_data": products,
                                        "product": storage_dict}
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
                                return {"success": True}

    @staticmethod
    def remove_reserve_msm(system_code, storage_id, count, order_number):
        with MongoConnection() as client:
            try:
                product_count = client.stocks_collection.count_documents(
                    {"systemCode": str(system_code), "stockId": str(storage_id)})

                if product_count > 0:
                    product = client.stocks_collection.find_one(
                        {"systemCode": str(system_code), "stockId": str(storage_id)},
                        {"_id": False})

                    if (int(product["reserve"]) + count) <= int(product["quantity"]):
                        update_data = {"$set": {"reserve": int(product["reserve"]) - count}}
                        query_data = {"systemCode": str(product["systemCode"]), "stockId": str(product["stockId"])}

                        return {"success": True, "query": query_data, "product": product,
                                "update_data": update_data}

                    else:
                        client.reserve_log_collection.insert_one(
                            {"systemCode": str(system_code), "stockId": str(storage_id), "orderNumber": order_number,
                             "message": "reserve bishtar az quantity",
                             "editDate": str(jdatetime.datetime.now()).split(".")[0]})
                        return {"success": False}

                else:
                    client.reserve_log_collection.insert_one(
                        {"systemCode": str(system_code), "stockId": str(storage_id), "orderNumber": order_number,
                         "message": "system code not found!", "editDate": str(jdatetime.datetime.now()).split(".")[0]})
                    return {"success": False}

            except:
                client.reserve_log_collection.insert_one(
                    {"systemCode": str(system_code), "stockId": str(storage_id), "orderNumber": order_number,
                     "message": "root exception", "editDate": str(jdatetime.datetime.now()).split(".")[0]})
                return {"success": False}


class addRemoveQuantity:
    @staticmethod
    def add_quantity(system_code, storage_id, count, customer_type, price):
        with MongoConnection() as client:
            quantity_count = client.product.count_documents({"system_code": system_code})
            if quantity_count > 0:
                product = client.product.find({"system_code": system_code}, {"_id": False})
                for products in product:
                    found_storage = False
                    for cusrsor, storage_dict in products['warehouse_details'].get(customer_type)['storages'].items():
                        if cusrsor == storage_id:
                            found_storage = True
                    if found_storage:
                        for cusrsor, storage_dict in products['warehouse_details'].get(customer_type)[
                            'storages'].items():
                            if cusrsor == storage_id:
                                storage_dict["quantity"] += count
                                storage_dict["regular"] = price
                                client.product.update_one({"system_code": system_code}, {"$set": products})
                                return {"success": True,
                                        "query": {"system_code": system_code},
                                        "replace_data": products,
                                        "storage_data": storage_dict}
                    else:
                        warehouse_detail = find_warehouse(storage_id)
                        client.product.update_one(
                            {"system_code": system_code},
                            {"$set": {f"warehouse_details.{customer_type}.storages.{storage_id}": {
                                "storage_id": storage_id,
                                "regular": price,
                                "reserved": 0,
                                "quantity": count,
                                "min_qty": 1,
                                "max_qty": 1,
                                "warehouse_state": warehouse_detail.get('state'),
                                "warehouse_city": warehouse_detail.get('city'),
                                "warehouse_state_id": str(warehouse_detail.get('state_id')),
                                "warehouse_city_id": warehouse_detail.get('city_id'),
                                "warehouse_label": warehouse_detail.get('warehouse_name')
                            }
                            }})
                        return {"success": True, "message": "عملیات مورد نظر با موفقیت انجام شد", "status_code": 200}
            else:
                client.reserve_log_collection.insert_one(
                    {"systemCode": str(system_code), "stockId": str(storage_id),
                     "message": "product not found in add qty",
                     "edit_date": str(jdatetime.datetime.now()).split(".")[0]})
                return {"success": False, "error": "سیستم کد مورد نظر وجود ندارد", "status_code": 404}

    @staticmethod
    def remove_quantity(system_code, storage_id, count, customer_type):
        with MongoConnection() as client:
            quantity_count = client.product.count_documents({"system_code": system_code})
            if quantity_count > 0:
                product = client.product.find({"system_code": system_code}, {"_id": False})
                for products in product:
                    for cusrsor, storage_dict in products['warehouse_details'].get(customer_type)['storages'].items():
                        if cusrsor == storage_id:
                            for cusrsor, storage_dict in products['warehouse_details'].get(customer_type)[
                                'storages'].items():
                                if cusrsor == storage_id:
                                    storage_dict["quantity"] -= count
                                    if storage_dict["quantity"] < 0:
                                        return {"success": False, "error": "تعداد از موجودی بیشتر است",
                                                "status_code": 404}
                                    client.product.update_one({"system_code": system_code}, {"$set": products})
                                    return {"success": True, "message": "عملیات مورد نظر با موفقیت انجام شد",
                                            "status_code": 200}
            else:
                client.reserve_log_collection.insert_one(
                    {"systemCode": str(system_code), "stockId": str(storage_id),
                     "message": "product not found in add qty",
                     "edit_date": str(jdatetime.datetime.now()).split(".")[0]})
                return {"success": False, "error": "سیستم کد مورد نظر وجود ندارد", "status_code": 404}
