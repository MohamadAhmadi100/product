import jdatetime

from app.helpers.mongo_connection import MongoConnection


def cardex(**kwargs):
    return {
        "storage_id": kwargs.get("storage_id"),
        "stock_name": "",
        "system_code": kwargs.get("system_code"),
        "incremental_id": kwargs.get("incremental_id"),
        "sku": kwargs.get("sku"),
        "type": kwargs.get("type"),
        "qty": kwargs.get("qty"),
        "old_quantity": kwargs.get("old_quantity"),
        "new_quantity": kwargs.get("new_quantity"),
        "old_reserve": kwargs.get("old_reserve"),
        "new_reserve": kwargs.get("new_reserve"),
        "edit_date": str(jdatetime.datetime.now()).split(".")[0],
        "imeis": kwargs.get("imeis"),
        "staff_user": kwargs.get("user"),
        "bi_flag": False
    }


def add_to_cardex(user_id, user_name, order_number, cardex_details):
    with MongoConnection() as client:
        for item in cardex_details:
            if item['incremental_id'] is None:
                item['incremental_id'] = order_number
            cardex = {"userId": user_id, "userName": user_name}
            cardex.update(item)
            client.cardex_collection.insert_one(cardex)
        return "cardex done"
