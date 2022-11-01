"""
- we have a master function(exit_order_handler) for handle logics thats called other functions
- in this route we need to check and update 3 collection that should have any state for handled rollback for any exeption
- created "rollback_object" after update in any product then use of that for update other collection and backe to befor state

"""
import jdatetime
from app.helpers.mongo_connection import MongoConnection
from pymongo import errors
import json
from app.helpers.telegram import admin_handler
import os

def exit_order_handler(order_number: int,
                       storage_id: str,
                       products: list,
                       staff_id: int,
                       staff_name: str,
                       customer_type: str) -> tuple:
    try:
        rollback_list = []
        rollback_flag = True
        error_message = None
        for product in products:
            imeis = product["imeis"]
            count = len(imeis)
            system_code = product["system_code"]
            # check and update product
            success, message = update_quantity(order_number,
                                               storage_id,
                                               system_code,
                                               count,
                                               staff_id,
                                               staff_name,
                                               "exitOrder",
                                               True,
                                               customer_type)

            if success:
                # create list of updated any product
                rollback_object = {

                    "orderNumber": order_number,
                    "storageId": storage_id,
                    "systemCode": system_code,
                    "count": count,
                    "staffId": staff_id,
                    "staffName": staff_name,
                    "imeis": imeis,
                    "customerType": customer_type
                }
                rollback_list.append(rollback_object)
            else:
                rollback_flag = False
                break
        if not rollback_flag:
            if rollback_list:
                # rolllbacking updated products and return error message
                rollback_products(rollback_list)
                return False, message

            return False, message
        # checking "archive" & "imeis" collection and rollback هn case of problem
        if not imeis_checking(rollback_list):
            rollback_products(rollback_list)
            return False, "خطا در چک imei"

        if not update_imeis(rollback_list):
            rollback_products(rollback_list)
            return False, "خطا در آپدیت imei"
        return True, rollback_list
    except:
        return False, "خطای سیستمی رخ داده است"


def update_quantity(order_number: int,
                    storage_id: str,
                    system_code: str,
                    count: int,
                    staff_id: int,
                    staff_name: str,
                    service_name: str,
                    flag: bool,
                    customer_type) -> tuple:
    """
    this function called in update and rollback action
    """
    try:
        # get product and object by storage_id and customer_type
        product = get_product_query(storage_id, system_code, customer_type)
        if not product:
            return False, "مغایرت در سیستم کد"
        qty_object = product.get("warehouse_details").get(customer_type).get("storages").get(storage_id)
        if not qty_object:
            return False, "مغایرت در اطلاعات"
        return product, qty_object
        # flag is False whene callled this func by rollback
        if flag:
            if objects["quantity"] < count or objects["reserved"] < count:
                return False, "مغایرت در تعداد موجودی"
        cardex = create_cardex_object(objects,
                                      order_number,
                                      storage_id,
                                      system_code,
                                      count,
                                      staff_id,
                                      staff_name,
                                      service_name,
                                      flag)
        # create cardex loge in any update for update and rollback
        if not cardex:
            return False, "خطا در آپدیت اطلاعات کاردکس"
        if not product_query(system_code, product):
            return False, "خطا در بروز رسانی موجودی"
        if not cardex_query(cardex):
            return False, "خطا در آپدیت کاردکس"
        return True, "موفق"
    except Exception as e:
        error = {
            "message": str(e),
            "functionName": "update_quantity",
            "date": str(jdatetime.datetime.now()).split(".")[0],
        }
        insert_error_log(error)

        return False, "خطای سیستمی رخ داده است"


def rollback_products(products: list) -> bool:
    try:
        for product in products:
            success, message = update_quantity(
                product["orderNumber"],
                product["storageId"],
                product["systemCode"],
                product["count"],
                product["staffId"],
                product["staffName"],
                "rollbackExitOrder",
                False,
                product["customerType"]
            )
            if not success:
                log = {
                    "type": "rollbackExitOrder",
                    "systemCode": product["systemCode"],
                    "customerType": product["customerType"],
                    "storageId": product["storageId"],
                    "count": product["count"],
                    "date": str(jdatetime.datetime.now()).split(".")[0],
                }
                insert_qty_log(log, "products")
                admin_handler("rollbackExitOrder")



    except Exception as e:
        error = {
            "message": str(e),
            "functionName": "rollback_products",
            "date": str(jdatetime.datetime.now()).split(".")[0],
        }
        insert_error_log(error)
        return False


def update_imeis(rollback_list: list) -> bool:
    """
    in this func update two collection (archive&imeis) and create list of updated object to rturn to befor state in case of problem
    """
    try:
        imei_list = []
        archive_list = []
        update_flag = True
        for pro in rollback_list:
            pro_imeis = pro["imeis"]
            success, returned_imeis = delete_imei_query(pro_imeis)
            if not success:
                add_imei_query(returned_imeis, pro["systemCode"], pro["storageId"], "imeis")
                update_flag = False
                break
            imei_list.append(pro)

            success, returned_archive = update_archive_query(pro_imeis, False)
            if not success:
                update_archive_query(returned_archive, True)
                update_flag = False
                break
            archive_list.append(pro)

        if update_flag:
            return True
        imeis_rollback(imei_list, archive_list)

        return False
    except Exception as e:
        error = {
            "message": str(e),
            "functionName": "update_imeis",
            "date": str(jdatetime.datetime.now()).split(".")[0],
        }
        insert_error_log(error)
        return False


def create_cardex_object(qty_object: dict,
                         order_number: int,
                         storage_id: str,
                         system_code: str,
                         count: int,
                         staff_id: int,
                         staff_name: str,
                         service_name: str,
                         flag: bool) -> bool:
    try:
        quantity_cardex_data = {
            "staff_id": staff_id,
            "staff_user": staff_name,
            "incremental_id": order_number,
            "storage_id": storage_id,
            "stockName": "",
            "system_code": system_code,
            "sku": "",
            "type": service_name,
            "qty": count,
            "old_quantity": qty_object["quantity"],
            "old_inventory": qty_object["inventory"],
            "old_reserve": qty_object["reserved"],
            "edit_date": str(jdatetime.datetime.now()).split(".")[0],
            "biFlag": False
        }
        # first creted object befor updated db and add updated field after update db for cardex log
        update_reserve_qty(qty_object, count, flag)
        quantity_cardex_data["new_quantity"] = qty_object["quantity"]
        quantity_cardex_data["new_inventory"] = qty_object["inventory"]
        quantity_cardex_data["new_reserve"] = qty_object["reserved"]
        return quantity_cardex_data

    except Exception as e:
        error = {
            "message": str(e),
            "functionName": "create_cardex_object",
            "date": str(jdatetime.datetime.now()).split(".")[0],
        }
        insert_error_log(error)
        return {}


def imeis_rollback(imeis: list, archives: list) -> bool:
    try:
        if imeis:
            for imei in imeis:
                add_imei_query(imei["imeis"], imei["systemCode"], imei["storageId"], "imeis")
        if archives:
            for pro in archives:
                update_archive_query(pro["imeis"], True)
    except Exception as e:
        error = {
            "message": str(e),
            "functionName": "imeis_rollback",
            "date": str(jdatetime.datetime.now()).split(".")[0],
        }
        insert_error_log(error)
        return False


def update_reserve_qty(qty_object: dict, count: int, flag: bool) -> bool:
    try:
        if flag:
            # for update
            qty_object["quantity"] -= count
            qty_object["inventory"] -= count
            qty_object["reserved"] -= count
        else:
            # for rollaback
            qty_object["quantity"] += count
            qty_object["inventory"] += count
            qty_object["reserved"] += count
        return True
    except Exception as e:
        error = {
            "message": str(e),
            "functionName": "update_reserve_qty",
            "date": str(jdatetime.datetime.now()).split(".")[0],
        }
        insert_error_log(error)
        return

    # checking functions


def imeis_checking(rollback_list: list) -> bool:
    try:
        for pro in rollback_list:
            pro_imeis = pro["imeis"]
            storage_id = pro["storageId"]
            system_code = pro["systemCode"]

            for imei in pro_imeis:
                if not check_imei_query(system_code, storage_id, imei, "imeis") or not check_archive_query(system_code,
                                                                                                           storage_id,
                                                                                                           imei):
                    return False
        return True
    except Exception as e:
        error = {
            "message": str(e),
            "functionName": "imeis_checking",
            "date": str(jdatetime.datetime.now()).split(".")[0],
        }
        insert_error_log(error)
        return False


def check_is_imei(system_code: str, storage_id: str, imeis: list) -> bool:
    try:
        for imei in imeis:
            if not check_imei_query(system_code, storage_id, imei, "imeis"):
                return False
        return True
    except Exception as e:
        error = {
            "message": str(e),
            "functionName": "check_is_imei",
            "date": str(jdatetime.datetime.now()).split(".")[0],
        }
        insert_error_log(error)
        return False


def check_in_archive(system_code: str, storage_id: str, imeis: list) -> bool:
    try:
        for imei in imeis:
            if not check_archive_query(system_code, storage_id, imei):
                return False
        return True
    except Exception as e:
        error = {
            "message": str(e),
            "functionName": "check_in_archive",
            "date": str(jdatetime.datetime.now()).split(".")[0],
        }
        insert_error_log(error)
        return False


# query functions


def insert_qty_log(new_data, record_type):
    with open(f"{os.getcwd()}/static_files/qty_logs.json", 'r+') as file:
        # First we load existing data into a dict.
        file_data = json.load(file)
        # Join new_data with file_data inside emp_details
        file_data[record_type].append(new_data)
        # Sets file's current position at offset.
        file.seek(0)
        # convert back to json.
        json.dump(file_data, file, indent=4)


def insert_error_log(new_error):
    with open(f"{os.getcwd()}/static_files/error_logs.json", 'r+') as file:
        # First we load existing data into a dict.
        file_data = json.load(file)
        # Join new_data with file_data inside emp_details
        file_data["errors"].append(new_error)
        # Sets file's current position at offset.
        file.seek(0)
        # convert back to json.
        json.dump(file_data, file, indent=4)
insert_error_log({"hj":9})

def add_imei_query(imeis: list, system_code: str, storage_id: str, record_type: str) -> bool:
    try:
        imei_list = []
        for imei in imeis:
            obj = {
                "imei": imei
            }
            imei_list.append(obj)

        with MongoConnection() as mongo:
            query = mongo.db.imeis.update_one(
                {"system_code": system_code, "storage_id": storage_id, "type": record_type},
                {"$addToSet": {
                    "imeis": {
                        "$each": imei_list}}}
            )

        if query.matched_count == 0:
            log = {
                "type": "addImei",
                "systemCode": system_code,
                "storageId": storage_id,
                "imeis": imei_list,
                "date": str(jdatetime.datetime.now()).split(".")[0],
            }
            insert_qty_log(log, "imeis")
            admin_handler("addImei")

    except Exception as e:
        error = {
            "message": str(e),
            "functionName": "add_imei_query",
            "date": str(jdatetime.datetime.now()).split(".")[0],
        }
        insert_error_log(error)
        return False
    except errors as mongo:
        error = {
            "message": str(mongo),
            "functionName": "add_imei_query",
            "date": str(jdatetime.datetime.now()).split(".")[0],
        }
        insert_error_log(error)
        return False


def get_product_query(storage_id: str, system_code: str, customer_type: str) -> tuple:
    try:
        with MongoConnection() as mongo:
            product = mongo.product.find_one({"system_code": system_code})
        if not product:
            # insert_bug_log(None, objects)
            return {}

            # insert_bug_log(None, objects)
        return product

    except Exception as e:
        error = {
            "message": str(e),
            "functionName": "get_product_query",
            "date": str(jdatetime.datetime.now()).split(".")[0],
        }
        insert_error_log(error)
        return {}
    except errors as mongo:
        error = {
            "message": str(mongo),
            "functionName": "get_product_query",
            "date": str(jdatetime.datetime.now()).split(".")[0],
        }
        insert_error_log(error)
        return {}


def update_archive_query(imeis: list, flag: bool) -> bool:
    try:
        check_flag = True
        archive_returned = []
        for imei in imeis:
            with MongoConnection() as mongo:
                query = mongo.db.archive.update_one({"articles.first": imei},
                                                    {"$set": {"articles.$.exist": flag}})
            if query.matched_count > 0:
                archive_returned.append(imei)
            else:
                if flag:
                    log = {
                        "type": "archive",
                        "imei": imei,
                        "date": str(jdatetime.datetime.now()).split(".")[0],
                    }
                    insert_qty_log(log, "archive")
                    admin_handler("archive")
                    pass

                else:
                    check_flag = False
                    break
        return check_flag, archive_returned

    except Exception as e:
        error = {
            "message": str(e),
            "functionName": "update_archive_query",
            "date": str(jdatetime.datetime.now()).split(".")[0],
        }
        insert_error_log(error)
        return False, []
    except errors as mongo:
        error = {
            "message": str(mongo),
            "functionName": "update_archive_query",
            "date": str(jdatetime.datetime.now()).split(".")[0],
        }
        insert_error_log(error)
        return False, []


def delete_imei_query(imeis: list) -> bool:
    try:
        flag = True
        imeis_returned = []
        for imei in imeis:
            with MongoConnection() as mongo:
                query = mongo.db.imeis.update_one({"imeis.imei": imei},
                                                  {"$pull": {
                                                      "imeis": {
                                                          "imei": imei
                                                      }}}
                                                  )
                if query.matched_count > 0:
                    imeis_returned.append(imei)
                else:
                    flag = False
                    break
        return flag, imeis_returned

    except Exception as e:
        error = {
            "message": str(e),
            "functionName": "delete_imei_query",
            "date": str(jdatetime.datetime.now()).split(".")[0],
        }
        insert_error_log(error)
        return False
    except errors as mongo:
        error = {
            "message": str(mongo),
            "functionName": "delete_imei_query",
            "date": str(jdatetime.datetime.now()).split(".")[0],
        }
        insert_error_log(error)
        return False


def product_query(system_code: str, product_object: dict) -> bool:
    try:
        with MongoConnection() as mongo:
            mongo.product.replace_one({"system_code": system_code}, product_object)
        return True

    except Exception as e:
        error = {
            "message": str(e),
            "functionName": "product_query",
            "date": str(jdatetime.datetime.now()).split(".")[0],
        }
        insert_error_log(error)
        return False
    except errors as mongo:
        error = {
            "message": str(mongo),
            "functionName": "product_query",
            "date": str(jdatetime.datetime.now()).split(".")[0],
        }
        insert_error_log(error)
        return False


def cardex_query(quantity_cardex_data: dict) -> bool:
    try:
        with MongoConnection() as mongo:
            mongo.db.cardex.insert_one(quantity_cardex_data)
        return True
    except Exception as e:
        error = {
            "message": str(e),
            "functionName": "cardex_query",
            "date": str(jdatetime.datetime.now()).split(".")[0],
        }
        insert_error_log(error)
        return False
    except errors as mongo:
        error = {
            "message": str(mongo),
            "functionName": "cardex_query",
            "date": str(jdatetime.datetime.now()).split(".")[0],
        }
        insert_error_log(error)
        return False


def check_imei_query(system_code: str, storage_id: str, imei: str, type: str) -> bool:
    try:
        with MongoConnection() as mongo:
            imeis = mongo.imeis.aggregate([
                {
                    '$unwind': {
                        'path': '$imeis'
                    }
                }, {
                    '$match': {

                        'system_code': system_code,
                        'imeis.imei': imei,
                        'storage_id': storage_id,
                        'type': type,

                    }
                }, {
                    '$project': {
                        'exist': '$imeis.imei',
                    }
                }, {
                    '$project': {
                        '_id': 0
                    }
                }
            ])

        if imeis.alive:
            exist = list(imeis)[0]
            if exist["exist"]:
                return True
            return False

        return False

    except Exception as e:
        error = {
            "message": str(e),
            "functionName": "check_imei_query",
            "date": str(jdatetime.datetime.now()).split(".")[0],
        }
        insert_error_log(error)
        return False
    except errors as mongo:
        error = {
            "message": str(mongo),
            "functionName": "check_imei_query",
            "date": str(jdatetime.datetime.now()).split(".")[0],
        }
        insert_error_log(error)
        return False


def check_archive_query(system_code: str, storage_id: str, imei: str) -> bool:
    try:

        with MongoConnection() as mongo:

            products = mongo.archive.aggregate([
                {
                    '$unwind': {
                        'path': '$articles'
                    }
                }, {
                    '$match': {

                        'system_code': system_code,
                        'articles.first': imei,
                        'articles.stockId': storage_id,
                        'articles.type': 'physical',
                        'articles.status': 'landed',
                    }
                }, {
                    '$project': {
                        'exist': '$articles.exist',
                    }
                }, {
                    '$project': {
                        '_id': 0
                    }
                }
            ])
        if products.alive:
            exist = list(products)[0]
            if exist["exist"]:
                return True
            return False

        return False
    except Exception as e:
        error = {
            "message": str(e),
            "functionName": "check_archive_query",
            "date": str(jdatetime.datetime.now()).split(".")[0],
        }
        insert_error_log(error)
        return False
    except errors as mongo:
        error = {
            "message": str(mongo),
            "functionName": "check_archive_query",
            "date": str(jdatetime.datetime.now()).split(".")[0],
        }
        insert_error_log(error)
        return False


# other router

def handle_imei_checking(system_code: str, storage_id: str, imei: str) -> tuple:
    try:
        if check_imei_query(system_code, storage_id, imei, "imeis") and check_archive_query(system_code, storage_id,
                                                                                            imei):
            return True, "کد معتبر است"
        return False, "کد نامعتبر است"
    except Exception:
        return False, "مشکل سیستمی رخ داده است"


def get_cardex_report(page: int,
                      per_page: int,
                      sort_name: str,
                      sort_type: str,
                      system_code: str,
                      storage_id: str,
                      incremental_id: int,
                      process_type: str) -> tuple:
    try:
        page = page if page else 1
        per_page = per_page if per_page else 15
        sort_type = sort_type if sort_type else "descend"
        sort_name = sort_name if sort_name else "edit_date"
        system_code = system_code if system_code else None
        storage_id = storage_id if storage_id else None
        incremental_id = incremental_id if incremental_id else None
        process_type = process_type if process_type else None

        page = page
        per = per_page
        skip = per * (page - 1)
        limit = per
        if sort_type == "descend":
            sort_type = -1
        else:
            sort_type = 1

        query = {}
        if system_code:
            query["system_code"] = system_code
        if storage_id:
            query["storage_id"] = storage_id
        elif incremental_id:
            query["incremental_id"] = incremental_id
        elif process_type:
            query["type"] = process_type
        with MongoConnection() as mongo:

            result = list(
                mongo.cardex_collection.find(query, {"_id": False}).sort(sort_name, sort_type).limit(limit).skip(skip))

            count = mongo.cardex_collection.count_documents(query)
            return True, {"totalCount": count, "result": result}
    except Exception:

        return False, {"totalCount": 0, "result": "خطای سیستمی رخ داده است"}


def get_imeis_report(system_code: str, storage_id: str) -> tuple:
    try:
        with MongoConnection() as mongo:

            result = mongo.imeis.find_one({"system_code": system_code, "storage_id": storage_id}, {"_id": False})
            if result:
                return True, result["imeis"]
            else:
                return False, "داده ای وجود ندارد"
    except Exception:

        return False, "خطای سیستمی رخ داده است"
