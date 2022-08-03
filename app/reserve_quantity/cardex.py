import jdatetime

from app.helpers.mongo_connection import MongoConnection


def cardex(**kwargs):
    return {
        "stockId": kwargs.get("storage_id"),
        "stockName": "",
        "systemCode": kwargs.get("system_code"),
        "orderNumber": kwargs.get("order_number"),
        "sku": kwargs.get("sku"),
        "type": kwargs.get("type"),
        "qty": kwargs.get("qty"),
        "oldQuantity": kwargs.get("oldQuantity"),
        "newQuantity": kwargs.get("newQuantity"),
        "oldReserve": kwargs.get("oldReserve"),
        "newRreserve": kwargs.get("newRreserve"),
        "editDate": str(jdatetime.datetime.now()).split(".")[0],
        "imeis": kwargs.get("imeis"),
        "staffUser": kwargs.get("user"),
        "biFlag": False
    }

