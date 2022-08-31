import jdatetime

from app.helpers.mongo_connection import MongoConnection
from app.helpers.warehouses import find_warehouse
from app.reserve_quantity.cardex import cardex


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


def add_msm_stocks(product, storage_id, supplier_name):
    with MongoConnection() as client:
        count = client.stocks_collection.count_documents(
            {"systemCode": product['system_code'], "stockId": storage_id})
        change_imei_to_msm_object = articles(product, storage_id)
        if count > 0:
            stocks = client.stocks_collection.find_one({"systemCode": product['system_code'], "stockId": storage_id})
            cardex_detail = cardex(
                storage_id=storage_id,
                system_code=stocks['systemCode'],
                sku=stocks['sku'],
                type="buying form",
                qty=product['count'],
                oldQuantity=stocks['quantity'],
                newQuantity=stocks['quantity'] + product['count'],
                oldReserve=stocks['reserve'],
                newRreserve=stocks['reserve'],
                imeis=product['imeis']
            )
            client.stocks_log_collection.insert_one(cardex_detail)
            client.stocks_collection.update_one({"systemCode": product['system_code'], "stockId": storage_id},
                                                {"$inc": {"quantity": product['count']},
                                                 "$push": {"imeis": {"$each": change_imei_to_msm_object}}}
                                                )
        else:
            cardex_detail = cardex(
                storage_id=storage_id,
                system_code=product['system_code'],
                sku=product['name'],
                type="buying form",
                qty=product['count'],
                oldQuantity=0,
                newQuantity=product['count'],
                oldReserve=0,
                newRreserve=0,
                imeis=product['imeis']
            )
            client.stocks_log_collection.insert_one(cardex_detail)
            client.stocks_collection.insert_one({
                "systemCode": product['system_code'],
                "sku": product['name'],
                "stockId": storage_id,
                "quantity": product['count'],
                "reserve": 0,
                "supplier": supplier_name,
                "cat": None,
                "brand": product['brand'],
                "model": product['model'],
                "color": product['color'],
                "seller": product['seller'],
                "guaranty": product['guaranty'],
                "packName": 'new product',
                "imeis": change_imei_to_msm_object
            })


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


def import_transfer_archive(products, src_warehouse, dst_warehouse, referral_number, staff_name):
    with MongoConnection() as client:
        transfer_stocks = []
        warehouse = find_warehouse(src_warehouse['storage_id'])['warehouses']
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
            objected_imei = {"imeis": imeis}
            client.imeis.update_one({"imeis.imei": imeis, "storage_id": "1000"}, {"$pull": {"imeis": {"imei": imeis}}})
            transfer_stocks.append(objected_imei)
        client.imeis.update_one({"system_code": products['system_code'], "storage_id": dst_warehouse['storage_id']},
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
                return {"success": False, "error": "کد مورد نظر قبلا خروج خورده است", "status_code": 400}
        else:
            return {"success": False, "error": "imei مورد نظر یافت نشد", "status_code": 400}

