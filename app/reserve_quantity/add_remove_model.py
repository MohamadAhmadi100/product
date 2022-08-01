import jdatetime

from app.helpers.mongo_connection import MongoConnection


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
                                        "product": storage_dict}
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


