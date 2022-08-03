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


def add_imeis(product, storage_id):
    with MongoConnection() as client:
        count = client.imeis.count_documents(
            {"system_code": product['system_code'], "storage_id": storage_id})
        if count > 0:
            client.imeis.update_one({"system_code": product['system_code'], "storage_id": storage_id},
                                    {"$push": {"imeis": {"$each": product['imeis']}}})
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
                "imeis": product['imeis']
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
