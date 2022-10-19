import jdatetime

from app.helpers.mongo_connection import MongoConnection
from app.helpers.warehouses import find_warehouse


def check_buying_imeis(product):
    with MongoConnection() as client:
        duplicate_imei = []
        for items in product['imeis']:
            count = client.product_archive.count_documents({"articles.first": items})
            if count > 0:
                duplicate_imei.append(items)
        if not duplicate_imei:
            return {"success": True}
        else:
            return {"success": False, "error": duplicate_imei, "status_code": 400}


def product_imeis(product):
    imei = []
    for item in product['imeis']:
        data = {
            "imei": item
        }
        imei.append(data)
    return imei


def add_imeis(product, storage_id):
    with MongoConnection() as client:
        count = client.imeis.count_documents(
            {"system_code": product['system_code'], "storage_id": storage_id})
        change_imeis_to_object = product_imeis(product)
        if count > 0:
            client.imeis.update_one({"system_code": product['system_code'], "storage_id": storage_id},
                                    {"$push": {"imeis": {"$each": change_imeis_to_object}}})
            return {"success": True}
        else:
            warehouse = find_warehouse(int(storage_id))
            client.imeis.insert_one({
                "type": "imeis",
                "system_code": product['system_code'],
                "name": product['name'],
                "brand": product['brand'],
                "model": product['model'],
                "color": product['color'],
                "guaranty": product['guaranty'],
                "seller": product['seller'],
                "stock_label": warehouse['warehouses'].get('warehouse_name'),
                "storage_id": str(warehouse['warehouses'].get('warehouse_id')),
                "imeis": change_imeis_to_object
            })
            return {"success": True}


def articles(product, dst_warehouse):
    warehouse = find_warehouse(dst_warehouse).get("warehouses")
    articles_deta = []
    for items in product['imeis']:
        data = {
            "first": items,
            "exist": True,
            "type": 'physical',
            "stockId": dst_warehouse,
            "stockName": warehouse['warehouse_name'],
            "stockLabel": warehouse['warehouse_name'],
            "stockState": warehouse['state'],
            "stockCity": warehouse['city'],
            "stockStateId": warehouse['state_id'],
            "stockCityId": warehouse['city_id'],
            "name": product['name'],
            "status": 'landed'
        }
        articles_deta.append(data)
    return articles_deta


def add_product_archive(product, referral_number, supplier, form_date, dst_warehouse):
    with MongoConnection() as client:
        client.product_archive.insert_one({
            "referral_number": referral_number,
            "system_code": product['system_code'],
            "name": product['name'],
            "supplier_name": supplier,
            "form_date": form_date,
            "insert_date": str(jdatetime.datetime.now()).split(".")[0],
            "unit_price": product['unit_price'],
            "sell_price": product['sell_price'],
            "articles": articles(product, dst_warehouse)
        })
        return {"success": True}


def add_warehouse_product(product, referral_number, supplier, form_date, dst_warehouse):
    with MongoConnection() as client:
        count = client.master_product_collection.count_documents(
            {"refferalNumber": referral_number, "partNumber": product['system_code']})
        if count > 0:
            return {"success": False, 'error': "فرم خرید قبلا ثبت شده.", "status_code": 400}
        client.master_product_collection.insert_one({
            "refferalNumber": referral_number,
            "partNumber": product['system_code'],
            "sku": product['name'],
            "quantity": product['count'],
            "supplier": supplier,
            "form_date": form_date,
            "cat": 'موبایل',
            "brand": 'سامسونگ',
            "model": 'A03s [32GB 3GB]',
            "color": 'Black',
            "seller": 'aasood',
            "guaranty": '18m aawaat',
            "registerDate": str(jdatetime.datetime.now()).split(".")[0],
            "packName": 'new product',
            "unit_price": product['unit_price'],
            "sell_price": product['sell_price'],
            "articles": articles(product, dst_warehouse),
            "isDoubleSim": False,
        })
        return {"success": True}


def export_transfer_archive(products, dst_warehouse, referral_number, staff_name):
    with MongoConnection() as client:
        count_imei = client.imeis.count_documents({"system_code": products['system_code'], "storage_id": "1000"})
        if count_imei == 0:
            transfer_object = client.imeis.find_one({"system_code": products['system_code']}, {"_id": False})
            transfer_object['stock_label'] = "انتقالی"
            transfer_object['storage_id'] = "1000"
            transfer_object['imeis'] = []
            client.imeis.insert_one(transfer_object)
        transfer_stocks = []
        for imeis in products['imeis']:
            client.product_archive.update_one({"articles.first": imeis}, {"$set": {
                "articles.$.transfer_detail":
                    [{
                        "to_storage": dst_warehouse['storage_id'],
                        "referral_number": referral_number,
                        "export_time": str(jdatetime.datetime.now()).split(".")[0],
                        "export_by": staff_name
                    }]
                ,
                "articles.$.status": "transfer"
            }})
            client.imeis.update_one({"imeis.imei": imeis}, {"$pull": {"imeis": {"imei": imeis}}})
            transfer_stocks.append(
                {"imei": imeis, "to_storage": dst_warehouse['storage_id'], "referral_number": referral_number})
        client.imeis.update_one({"system_code": products['system_code'], "storage_id": "1000"},
                                {"$push": {"imeis": {"$each": transfer_stocks}}})
        return {"success": True}


def export_transfer_dealership(system_code, imeis, dealership_detail, referral_number):
    with MongoConnection() as client:
        count_imei = client.imeis.count_documents({"system_code": system_code, "storage_id": "2000"})
        if count_imei == 0:
            transfer_object = client.imeis.find_one({"system_code": system_code}, {"_id": False})
            transfer_object['stock_label'] = "نماینده"
            transfer_object['storage_id'] = "2000"
            transfer_object['imeis'] = []
            client.imeis.insert_one(transfer_object)
        transfer_stocks = []
        for imei in imeis:
            client.product_archive.update_one({"articles.first": imei}, {"$set": {
                "articles.$.dealership_detail":
                    [{
                        "to_dealership": dealership_detail['dealershipId'],
                        "referral_number": referral_number,
                        "export_time": str(jdatetime.datetime.now()).split(".")[0],
                    }]
                ,
                "articles.$.status": "dealership",
                "articles.$.exist": False
            }})
            client.imeis.update_one({"imeis.imei": imei}, {"$pull": {"imeis": {"imei": imei}}})
            transfer_stocks.append(
                {"imei": imei, "to_storage": "2000", "referral_number": referral_number})
        client.imeis.update_one({"system_code": system_code, "storage_id": "2000"},
                                {"$push": {"imeis": {"$each": transfer_stocks}}})
        return {"success": True}


"""
dealership_detail = {
    "dealershipPhoneNumber": str,
    "dealershipId": str,

}"""


def import_transfer_archive(products, src_warehouse, dst_warehouse, referral_number, staff_name):
    with MongoConnection() as client:
        transfer_stocks = []
        warehouse = find_warehouse(dst_warehouse['storage_id'])['warehouses']
        for imeis in products['imeis']:
            client.product_archive.update_one({"articles.first": imeis},
                                              {"$set": {
                                                  "articles.$.status": "landed",
                                                  "articles.$.stockId": dst_warehouse['storage_id'],
                                                  "articles.$.stockName": warehouse['warehouse_name'],
                                                  "articles.$.stockLabel": warehouse['warehouse_name'],
                                                  "articles.$.stockState": warehouse['state'],
                                                  "articles.$.stockCity": warehouse['city'],
                                                  "articles.$.stockStateId": warehouse['state_id'],
                                                  "articles.$.stockCityId": warehouse['city_id'],
                                              },
                                                  "$push": {"articles.$.transfer_detail": {
                                                      "from_storage": src_warehouse['storage_id'],
                                                      "referral_number": referral_number,
                                                      "import_time": str(jdatetime.datetime.now()).split(".")[0],
                                                      "import_by": staff_name
                                                  }
                                                  }})
            objected_imei = {"imei": imeis}
            client.imeis.update_one({"imeis.imei": imeis, "storage_id": "1000"}, {"$pull": {"imeis": {"imei": imeis}}})
            transfer_stocks.append(objected_imei)
        count = client.imeis.count_documents(
            {"system_code": products['system_code'], "storage_id": dst_warehouse['storage_id']})
        if count > 0:
            client.imeis.update_one(
                {"system_code": products['system_code'], "storage_id": dst_warehouse['storage_id']},
                {"$push": {"imeis": {"$each": transfer_stocks}}})
        else:
            client.imeis.insert_one({
                "type": 'imeis',
                "system_code": products['system_code'],
                "name": products['name'],
                "brand": products['brand'],
                "model": products['model'],
                "color": products['color'],
                "guaranty": products['guaranty'],
                "seller": products['seller'],
                "stock_label": warehouse['warehouse_name'],
                "storage_id": str(warehouse['warehouse_id']),
                "imeis": []
            })
            client.imeis.update_one(
                {"system_code": products['system_code'], "storage_id": dst_warehouse.get('storage_id')},
                {"$push": {"imeis": {"$each": transfer_stocks}}})
        return {"success": True}


def check_transfer_imei(imei, transfer_object):
    with MongoConnection() as clinet:
        check_imei = clinet.product_archive.aggregate([
            {
                '$match': {
                    'articles.first': imei
                }
            }, {
                '$unwind': {
                    'path': '$articles'
                }
            }, {
                '$match': {
                    'articles.first': imei
                }
            }, {
                '$project': {
                    'exist': '$articles.exist',
                    'storage': '$articles.stockId',
                    'status': '$articles.status'
                }
            }, {
                '$project': {
                    '_id': 0
                }
            }
        ])
        if check_imei.alive:
            check_data = list(check_imei)[0]
            if check_data.get("exist"):
                if transfer_object['status_type'] == "submit":
                    if check_data.get("storage") == transfer_object['src_warehouse']['storage_id']:
                        return {"success": True, "status_code": 200}
                    else:
                        return {"success": False, "error": "کد مورد نظر در انبار دیگری موجود است", "status_code": 400}
                elif transfer_object['status_type'] == "transfer":
                    if check_data.get("status") == "transfer":
                        imeis_check = clinet.imeis.aggregate([
                            {
                                '$unwind': {
                                    'path': '$imeis'
                                }
                            }, {
                                '$match': {
                                    'imeis.imei': imei
                                }
                            }, {
                                '$project': {
                                    '_id': 0,
                                    'to_storage': '$imeis.to_storage',
                                    'referral_number': '$imeis.referral_number'
                                }
                            }
                        ])
                        if imeis_check.alive:
                            imeis_check = list(imeis_check)[0]
                            if check_data.get("storage") == transfer_object['src_warehouse'][
                                'storage_id'] and imeis_check.get("to_storage") == transfer_object['dst_warehouse'][
                                'storage_id']:
                                return {"success": True, "status_code": 200}
                            else:
                                return {"success": False, "error": "کد مورد نظر در انبار دیگری موجود است",
                                        "status_code": 400}
                        else:
                            return {"success": False, "error": "کد مورد نظر در قسمت خروج به مشکل خورده است",
                                    "status_code": 400}
                    else:
                        return {"success": False, "error": "کد مورد نظر در قسمت خروج به مشکل خورده است",
                                "status_code": 400}
            else:
                return {"success": False, "error": "کد مورد نظر قبلا خروج خورده است", "status_code": 400}
        else:
            return {"success": False, "error": "imei مورد نظر یافت نشد", "status_code": 400}


def return_order(imei, system_code, storage_id):
    with MongoConnection() as clinet:
        count_imei = clinet.imeis.count_documents({"imeis.imei": imei, "storage_id": storage_id})
        count_archive = clinet.archive.count_documents({"articles.first": imei})
        if count_archive == 0:
            return {"success": False, "error": "کد مورد نظر یافت نشد"}

        clinet.product_archive.update_one({"articles.first": imei},
                                          {"$set": {
                                              "articles.$.exist": True,
                                              "articles.$.return_imei": True,
                                          }})

        if count_imei == 0:
            clinet.imeis.update_one(
                {"system_code": system_code, "storage_id": storage_id},
                {"$push": {"imeis": {"$each": [{"imei": imei}]}}})
        return {"success": True}
