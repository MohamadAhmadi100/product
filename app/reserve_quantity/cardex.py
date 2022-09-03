import jdatetime

from app.helpers.mongo_connection import MongoConnection


def cardex(**kwargs):
    return {
        "stockId": kwargs.get("storage_id"),
        "stockName": "",
        "systemCode": kwargs.get("system_code"),
        "incremental_id": kwargs.get("incremental_id"),
        "sku": kwargs.get("sku"),
        "type": kwargs.get("type"),
        "qty": kwargs.get("qty"),
        "old_quantity": kwargs.get("oldQuantity"),
        "new_quantity": kwargs.get("newQuantity"),
        "old_reserve": kwargs.get("oldReserve"),
        "new_reserve": kwargs.get("newReserve"),
        "edit_date": str(jdatetime.datetime.now()).split(".")[0],
        "imeis": kwargs.get("imeis"),
        "staff_user": kwargs.get("user"),
        "bi_flag": False
    }


def add_to_cardex(user_id, user_name, order_number, cardex_details):
    with MongoConnection() as client:
        for item in cardex_details:
            cardex = {"userId": user_id, "userName": user_name, "orderNumber": order_number}
            cardex.update(item)
            client.cardex_collection.insert_one(cardex)
        return "cardex done"
