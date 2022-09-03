import jdatetime
from app.helpers.mongo_connection import MongoConnection


def exit_order_handler(order_number,
                       storage_id,
                       products,
                       staff_id,
                       staff_name):
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
                                           True)

        if success:

            rollback_object = create_rollback(order_number,
                                              storage_id,
                                              system_code,
                                              count,
                                              staff_id,
                                              staff_name,
                                              imeis
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

    if not checking_imeis(rollback_list):
        rollback_products(rollback_list)
        return False, "مشکل در چک imei"

    if not update_imeis(rollback_list):
        rollback_products(rollback_list)
        return False, "مشکل در آپدیت imei"
    # return True, rollback_list
    return True, rollback_list


def update_quantity(order_number,
                    storage_id,
                    system_code,
                    count,
                    staff_id,
                    staff_name,
                    service_name,
                    flag):
    try:
        product, objects = get_product(storage_id, system_code)
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
                    imeis
                    ):
    try:
        rollback_object = {

            "orderNumber": order_number,
            "storageId": storage_id,
            "systemCode": system_code,
            "count": count,
            "staffId": staff_id,
            "staffName": staff_name,
            "imeis": imeis
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

            update_quantity(order_number,
                            storage_id,
                            system_code,
                            count,
                            staff_id,
                            staff_name,
                            "rollbackExitOrder",
                            False)
        return True
    except:
        return False


def checking_imeis(rollback_list):
    for pro in rollback_list:
        pro_imeis = pro["imeis"]
        storage_id = pro["storageId"]
        system_code = pro["systemCode"]
        check_imei_collection = check_is_imei(system_code, storage_id, pro_imeis)
        check_archive_collection = archive_checking(system_code, storage_id, pro_imeis)
        if not check_imei_collection or not check_archive_collection:
            return False
    return True


def update_imeis(rollback_list):
    try:
        imei_list = []
        archive_list = []
        update_flag = True
        for pro in rollback_list:
            pro_imeis = pro["imeis"]
            if not delete_imei(pro_imeis):
                update_flag = False
                break
            imei_list.append(pro)

            if not update_archive(pro_imeis, False):
                update_flag = False
                break
            archive_list.append(pro)

        if not update_flag:
            if len(archive_list) > 0 or len(imei_list) > 0:
                if not rollback_update_imeis(imei_list, archive_list):
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
            "userId": staff_id,
            "userName": staff_name,
            "orderNumber": order_number,
            "stockId": storage_id,
            "stockName": "",
            "systemCode": system_code,
            "sku": "",
            "type": service_name,
            "qty": count,
            "oldQuantity": qty_object["quantity"],
            "oldReserve": qty_object["reserved"],
            "createdDate": str(jdatetime.datetime.now()).split(".")[0],
            "biFlag": False
        }
        update_reserve_qty(qty_object, count, flag)
        quantity_cardex_data["newQuantity"] = qty_object["quantity"]
        quantity_cardex_data["newReserve"] = qty_object["reserved"]
        return quantity_cardex_data

    except Exception:
        return False


def cardex_query(quantity_cardex_data):
    try:
        with MongoConnection() as mongo:
            mongo.db.cardex.insert_one(quantity_cardex_data)
        return True
    except Exception:
        return False


def quantity_checking(quantity, reserved, count):
    if quantity < count or reserved < count:
        return False
    return True


def product_query(system_code, product_object):
    try:
        with MongoConnection() as mongo:
            mongo.product.replace_one({"system_code": system_code}, product_object)
        return True
    except:
        return False


def create_archive_obj(imeis):
    imei_obj = []
    for i in imeis:
        obj = {
            "imei": i
        }
        imei_obj.append(obj)
    return imei_obj


def rollback_update_imeis(imeis: list, archives: list):
    try:
        if len(imeis) > 0:

            for imei in imeis:
                if not insert_imei(imei["imeis"], imei["systemCode"], imei["storageId"], "imeis"):
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


def archive_checking(system_code, storage_id, imeis):
    try:
        for imei in imeis:
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
                if not exist["exist"]:
                    return False
            else:
                return False
        return True

    except Exception:
        return False


def check_is_imei(system_code, storage_id, imeis):
    try:
        imeis_collection = get_imei(system_code, storage_id)
        if imeis:
            check = []
            for imei in imeis_collection["imeis"]:
                if imei["imei"] in imeis:
                    check.append(imei["imei"])
            if len(imeis) != len(check):
                return False
            return True
        else:
            return False
    except:
        return False


def get_imei(system_code, storage_id):
    try:
        with MongoConnection() as mongo:
            products = mongo.imeis.find_one(
                {"system_code": str(system_code), "storage_id": str(storage_id), "type": "imeis"})
            if products:
                return products
            else:
                return False
    except:
        return False


def delete_imei(imeis: list):
    try:
        for imei in imeis:
            with MongoConnection() as mongo:
                mongo.db.imeis.update_one({"imeis.imei": imei},
                                                  {"$pull": {
                                                      "imeis": {
                                                          "imei": imei
                                                      }}}
                                                  )
            # if query.matched_count > 0:
            #     return True
        return True
    except:
        return False


def update_archive(imeis: list, flag):
    try:

        for imei in imeis:
            response = archive_query(imei, {"articles.$.exist": flag})
            if not response:
                return False
        return True
    except:
        return False


def archive_query(imei, new_object):
    try:
        with MongoConnection() as mongo:
            query = mongo.db.archive.update_one({"articles.first": imei},
                                                {"$set": new_object})
        if query.matched_count > 0:
            return True
        return False

    except:
        return False


def insert_imei(imei: list, system_code: str, storage_id: str, record_type: str):
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


def get_product(storage_id, system_code):
    with MongoConnection() as mongo:
        product = mongo.product.find_one({"system_code": system_code})
    if not product:
        # insert_bug_log(None, objects)
        return False, False
    qty_object = product.get("warehouse_details").get("B2B").get("storages").get(storage_id)
    if not qty_object:
        # insert_bug_log(None, objects)
        return False, False
    return product, qty_object


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

# def insert_bug_log(storage_dict, objects):
#     try:
#         quantity_log_data = {
#             "userId": objects.get("userId", ""),
#             "userName": objects.get("userName", ""),
#             "orderNumber": objects.get("orderNumber", ""),
#             "stockId": objects.get("stockId", ""),
#             "stockName": objects.get("stockName", ""),
#             "systemCode": objects.get("systemCode", ""),
#             "sku": objects.get("sku", ""),
#             "type": objects.get("serviceName", ""),
#             "qty": objects.get("qty", ""),
#             "createdDate": str(jdatetime.datetime.now()).split(".")[0],
#             "to_stock": objects.get("qty", ""),
#             "biFlag": False
#         }
#         if storage_dict:
#             quantity_log_data["quantity"] = storage_dict["quantity"]
#             quantity_log_data["reserve"] = storage_dict["reserved"]
#
#         client.bug_log.insert_one(quantity_log_data)
#
#     except Exception as e:
#         print(str(e))
