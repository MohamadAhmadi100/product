import jdatetime
from app.helpers.mongo_connection import MongoConnection


def exit_order_handler(order_number: int,
                       storage_id,
                       products,
                       staff_id,
                       staff_name,
                       customer_type):
    try:
        rollback_list = []
        rollback_flag = True
        error_message = None
        for product in products:
            imeis = product["imeis"]
            count = len(imeis)
            system_code = product["system_code"]

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

                rollback_object = create_rollback(order_number,
                                                  storage_id,
                                                  system_code,
                                                  count,
                                                  staff_id,
                                                  staff_name,
                                                  imeis,
                                                  customer_type
                                                  )
                rollback_list.append(rollback_object)
            else:
                rollback_flag = False
                error_message = message
                break
        if not rollback_flag:
            if len(rollback_list) > 0:
                rollback_products(rollback_list)
                return False, error_message

            return False, error_message

        if not imeis_checking(rollback_list):
            rollback_products(rollback_list)
            return False, "مشکل در چک imei"

        if not update_imeis(rollback_list):
            rollback_products(rollback_list)
            return False, "مشکل در آپدیت imei"
        return True, rollback_list
    except:
        return False, "خطای سیستمی رخ داده است"


def update_quantity(order_number,
                    storage_id,
                    system_code,
                    count,
                    staff_id,
                    staff_name,
                    service_name,
                    flag,
                    customer_type):
    try:
        product, objects = get_product_query(storage_id, system_code, customer_type)
        if not objects:
            return False, "مغایرت در سیستم کد"
        if flag:
            if not quantity_checking(objects["quantity"], objects["reserved"], count):
                return False, "مشکل در تعداد موجودی"
        cardex = create_cardex_object(objects,
                                      order_number,
                                      storage_id,
                                      system_code,
                                      count,
                                      staff_id,
                                      staff_name,
                                      service_name,
                                      flag)

        if not cardex:
            return False, "مشکل در آپدیت کاردکس"
        if not product_query(system_code, product):
            return False, "مشکل در بروز رسانی موجودی"
        if not cardex_query(cardex):
            return False, "مشکل در آپدیت کاردکس"
        return True, "موفق"
    except:
        return False, "خطای سیستمی"


def create_rollback(order_number,
                    storage_id,
                    system_code,
                    count,
                    staff_id,
                    staff_name,
                    imeis,
                    customer_type
                    ):
    try:
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
        return rollback_object
    except:
        return False


def rollback_products(products: list):
    try:
        for product in products:
            order_number = product["orderNumber"]
            storage_id = product["storageId"]
            system_code = product["systemCode"]
            count = product["count"]
            staff_id = product["staffId"]
            staff_name = product["staffName"]
            customer_type = product["customerType"]

            update_quantity(order_number,
                            storage_id,
                            system_code,
                            count,
                            staff_id,
                            staff_name,
                            "rollbackExitOrder",
                            False,
                            customer_type
                            )
        return True
    except:
        return False


def update_imeis(rollback_list):
    try:
        imei_list = []
        archive_list = []
        update_flag = True
        for pro in rollback_list:
            pro_imeis = pro["imeis"]
            if not delete_imei_query(pro_imeis):
                update_flag = False
                break
            imei_list.append(pro)

            if not update_archive(pro_imeis, False):
                update_flag = False
                break
            archive_list.append(pro)

        if not update_flag:
            if len(archive_list) > 0 or len(imei_list) > 0:
                if not imeis_rollback(imei_list, archive_list):
                    # TOdo insert log
                    return False

                return False
            else:
                return False

        return True
    except:
        return False


def create_cardex_object(qty_object,
                         order_number,
                         storage_id,
                         system_code,
                         count,
                         staff_id,
                         staff_name,
                         service_name,
                         flag):
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
            "old_reserve": qty_object["reserved"],
            "edit_date": str(jdatetime.datetime.now()).split(".")[0],
            "biFlag": False
        }
        update_reserve_qty(qty_object, count, flag)
        quantity_cardex_data["new_quantity"] = qty_object["quantity"]
        quantity_cardex_data["new_reserve"] = qty_object["reserved"]
        return quantity_cardex_data

    except Exception:
        return False


def create_archive_obj(imeis):
    imei_obj = []
    for i in imeis:
        obj = {
            "imei": i
        }
        imei_obj.append(obj)
    return imei_obj


def imeis_rollback(imeis: list, archives: list):
    try:
        if len(imeis) > 0:

            for imei in imeis:
                if not add_imei_query(imei["imeis"], imei["systemCode"], imei["storageId"], "imeis"):
                    # TOdo insert log
                    return False
        if len(archives) > 0:
            for pro in archives:
                if not update_archive(pro["imeis"], True):
                    # TOdo insert log
                    return False
        return True
    except:
        return False


def update_archive(imeis: list, flag):
    try:

        for imei in imeis:
            response = update_archive_query(imei, {"articles.$.exist": flag})
            if not response:
                return False
        return True
    except:
        return False


def update_reserve_qty(qty_object, count, flag):
    try:
        if flag:
            qty_object["quantity"] -= count
            qty_object["reserved"] -= count
        else:
            qty_object["quantity"] += count
            qty_object["reserved"] += count
        return True
    except:
        return False


# checking functions
def imeis_checking(rollback_list):
    flag = True
    for pro in rollback_list:
        pro_imeis = pro["imeis"]
        storage_id = pro["storageId"]
        system_code = pro["systemCode"]
        check_imei_collection = check_is_imei(system_code, storage_id, pro_imeis)
        check_archive_collection = check_in_archive(system_code, storage_id, pro_imeis)
        if not check_imei_collection or not check_archive_collection:
            flag = False
            break
    if flag:
        return True
    return False


def check_is_imei(system_code, storage_id, imeis):
    try:
        for imei in imeis:
            if not check_imei_query(system_code, storage_id, imei, "imeis"):
                return False
        return True
    except:
        return False


def check_in_archive(system_code, storage_id, imeis):
    try:
        for imei in imeis:
            if not check_archive_query(system_code, storage_id, imei):
                return False
        return True
    except Exception:
        return False


def quantity_checking(quantity, reserved, count):
    if quantity < count or reserved < count:
        return False
    return True


# query functions

def add_imei_query(imei: list, system_code: str, storage_id: str, record_type: str):
    try:
        imei_list = create_archive_obj(imei)
        with MongoConnection() as mongo:
            query = mongo.db.imeis.update_one(
                {"system_code": system_code, "storage_id": storage_id, "type": record_type},
                {"$addToSet": {
                    "imeis": {
                        "$each": imei_list}}}
            )

        if query.matched_count > 0:
            return True
        return False
    except:
        return False


def get_product_query(storage_id, system_code, customer_type):
    with MongoConnection() as mongo:
        product = mongo.product.find_one({"system_code": system_code})
    if not product:
        # insert_bug_log(None, objects)
        return False, False
    qty_object = product.get("warehouse_details").get(customer_type).get("storages").get(storage_id)
    if not qty_object:
        # insert_bug_log(None, objects)
        return False, False
    return product, qty_object


def update_archive_query(imei, new_object):
    try:
        with MongoConnection() as mongo:
            query = mongo.db.archive.update_one({"articles.first": imei},
                                                {"$set": new_object})
        if query.matched_count > 0:
            return True
        return False

    except:
        return False


def delete_imei_query(imeis: list):
    try:
        for imei in imeis:
            with MongoConnection() as mongo:
                mongo.db.imeis.update_one({"imeis.imei": imei},
                                          {"$pull": {
                                              "imeis": {
                                                  "imei": imei
                                              }}}
                                          )

        return True
    except:
        return False


def product_query(system_code, product_object):
    try:
        with MongoConnection() as mongo:
            mongo.product.replace_one({"system_code": system_code}, product_object)
        return True
    except:
        return False


def cardex_query(quantity_cardex_data):
    try:
        with MongoConnection() as mongo:
            mongo.db.cardex.insert_one(quantity_cardex_data)
        return True
    except Exception:
        return False


def check_imei_query(system_code, storage_id, imei, type):
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

    except:
        return False


def check_archive_query(system_code, storage_id, imei):
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
    except:
        return False


# other router

def handle_imei_checking(system_code, storage_id, imei):
    try:
        imei_check = check_imei_query(system_code, storage_id, imei, "imeis")
        archive_check = check_archive_query(system_code, storage_id, imei)

        if imei_check and archive_check:
            return True, "موفق"
        return False, "ناموفق"
    except:
        return False, "مشکل سیستمی رخ داده است"


def get_cardex_report(page,
                      per_page,
                      sort_name,
                      sort_type, system_code, storage_id, incremental_id, process_type):
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
    except:

        return False, {"totalCount": 0, "result": "خطای سیستمی رخ داده است"}


def get_imeis_report(system_code, storage_id):
    try:
        with MongoConnection() as mongo:

            result = mongo.imeis.find_one({"system_code": system_code, "storage_id": storage_id}, {"_id": False})
            if result:
                return True, result["imeis"]
            else:
                return False, "داده ای وجود ندارد"
    except:

        return False, "خطای سیستمی رخ داده است"
