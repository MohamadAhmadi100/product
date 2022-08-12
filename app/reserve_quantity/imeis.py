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


def add_product_details(product, referral_number, supplier, form_date, dst_warehouse):
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
        change_imei_to_msm_object = articles(product,storage_id)
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
