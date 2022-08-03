from app.helpers.warehouses import warehouses
from app.reserve_quantity.add_remove_model import addRemoveQuantity
from app.reserve_quantity.cardex import cardex
from app.reserve_quantity.imeis import *
from app.reserve_quantity.route_actions import Reserve

"""
order
"""


def remove_from_reserve(order):
    order_model = Reserve(dict(order))
    add_cardex_to_msm, add_cardex_to_quantity = list(), list()
    for item in order_model.order_data:
        result = order_model.remove_reserve_cancel(item.get("system_code"), item.get("storage_id"), item.get("count"),
                                                   item.get("customer_type"), item.get("sku"), item.get("order_number"))
        add_cardex_to_msm.append(result.get("msm"))
        add_cardex_to_quantity.append(result.get("quantity"))
        if result.get("success") is False:
            return result
    try:
        Reserve.cardex(order["customer"].get("id"), order["customer"].get("fullName"), order.get("orderNumber"),
                       add_cardex_to_quantity)
        Reserve.msm_log(order["customer"].get("id"), order["customer"].get("fullName"), order.get("orderNumber"),
                        add_cardex_to_msm)
        return {'success': True, 'message': 'done', 'status_code': 200}
    except:
        return {'success': False, 'message': 'log error', 'status_code': 409}


def add_to_reserve(order):
    order_model = Reserve(dict(order))
    check_data, add_cardex_to_msm, add_cardex_to_quantity = list(), list(), list()
    for item in order_model.order_data:
        result = order_model.add_to_reserve_order(item.get("system_code"), item.get("storage_id"), item.get("count"),
                                                  item.get("customer_type"), item.get("sku"), item.get("order_number"))

        data_for_check = (item, result.get("success"))
        check_data.append(data_for_check)
        add_cardex_to_msm.append(result.get("msm"))
        add_cardex_to_quantity.append(result.get("quantity"))
    checked = all(elem[1] for elem in check_data)
    if checked:
        try:
            Reserve.cardex(order["customer"].get("id"), order["customer"].get('fullName'), order.get("orderNumber"),
                           add_cardex_to_quantity)
            Reserve.msm_log(order["customer"].get("id"), order["customer"].get('fullName'), order.get("orderNumber"),
                            add_cardex_to_msm)
            return {'success': True, 'message': 'done', 'status_code': 200}
        except:
            return {'success': False, 'message': 'log error', 'status_code': 409}
    else:
        for data in check_data:
            if data[1] is True:
                result = order_model.remove_reserve_cancel(data[0].get("system_code"), data[0].get("storage_id"),
                                                           data[0].get("count"), data[0].get("customer_type"),
                                                           data[0].get("sku"), data[0].get("order_number"))
                if result.get("success") is False:
                    return result
        return {'success': False, 'message': 'operation unsuccessful', "check_data": check_data, 'status_code': 200}


def remove_reserve_edit(edited_object, order_number, customer_id, customer_type, customer_name):
    add_cardex_to_msm, add_cardex_to_quantity = list(), list()

    for item in edited_object:
        result = Reserve.remove_reserve_edit_order(item.get("systemCode"), item.get("storageId"),
                                                   (int(item.get("oldCount")) - int(item.get("newCount"))),
                                                   customer_type, item.get("sku"), item.get("order_number"))
        if result.get("success") is False:
            return result
        add_cardex_to_msm.append(result.get("msm"))
        add_cardex_to_quantity.append(result.get("quantity"))

    try:
        Reserve.cardex(customer_id, customer_name, order_number, add_cardex_to_quantity)
        Reserve.msm_log(customer_id, customer_name, order_number, add_cardex_to_msm)
        return {'success': True, 'message': 'done', 'status_code': 200}
    except:
        return {'success': False, 'message': 'log error', 'status_code': 409}


"""
dealership
"""


def add_to_reserve_dealership(referral_number, customer_id, customer_type, data):
    check_data, add_cardex_to_msm, add_cardex_to_quantity = list(), list(), list()
    for item in data.get("products"):
        result = Reserve.add_to_reserve_dealership(item.get("system_code"), item.get("storage_id"), item.get("count"),
                                                   customer_type[0], item.get("name"), referral_number)

        data_for_check = (item, result.get("success"))
        check_data.append(data_for_check)
        add_cardex_to_msm.append(result.get("msm"))
        add_cardex_to_quantity.append(result.get("quantity"))
    checked = all(elem[1] for elem in check_data)
    if checked:
        try:

            Reserve.cardex(customer_id, None, referral_number,
                           add_cardex_to_quantity)
            Reserve.msm_log(customer_id, None, referral_number,
                            add_cardex_to_msm)
            return {'success': True, 'message': 'done', 'status_code': 200}
        except:
            return {'success': False, 'message': 'log error', 'status_code': 409}
    else:
        for element in check_data:
            if element[1] is True:
                result = Reserve.remove_reserve_cancel(element[0].get("systemCode"), element[0].get("storageId"),
                                                       element[0].get("count"), element[0].get("customer_type"),
                                                       element[0].get("name"), referral_number)
                if result.get("success") is False:
                    return result
        return {'success': False, 'message': 'operation unsuccessful', "check_data": check_data, 'status_code': 200}


"""
warehouse
"""


def warehouse_buying(product, dst_warehouse, referral_number, supplier_name, form_date, customer_type):
    check = check_buying_imeis(product)
    if check.get("success"):
        master_product = add_warehouse_product(product, referral_number, supplier_name, form_date, dst_warehouse)
        if master_product.get("success"):
            product_result = addRemoveQuantity.add_quantity(product['system_code'], dst_warehouse, product['count'],
                                                            customer_type, product['sell_price'])
            if product_result.get("success"):
                add_msm_stocks(product, dst_warehouse, supplier_name)
                imei = add_imeis(product, dst_warehouse)
                archive = add_product_details(product, referral_number, supplier_name, form_date, dst_warehouse)
                if imei and archive:
                    cardex_detail = cardex(
                        storage_id=dst_warehouse,
                        system_code=product['system_code'],
                        order_number=referral_number,
                        qty=product['count'],
                        sku=product['name'],
                        type="buying form",
                        imeis=product['imeis'],
                        oldQuantity=product_result['cardex_data'].get("old_quantity"),
                        newQuantity=product_result['cardex_data'].get("new_quantity"),
                        oldReserve=product_result['cardex_data'].get('reserve'),
                        newRreserve=product_result['cardex_data'].get('reserve')
                    )
                    with MongoConnection() as client:
                        client.cardex_collection.insert_one(cardex_detail)
                    product_result.pop("cardex_data")
                    return product_result
            else:
                return product_result
        else:
            return master_product
    else:
        return check


def export_transfer_form(product, src_warehouse, referral_number):
    product_result = addRemoveQuantity.remove_quantity(product['system_code'], src_warehouse, product['count'],
                                                       product['customer_type'])
    # TODO imeis
    if product_result.get("success"):
        cardex_detail = cardex(
            storage_id=src_warehouse,
            system_code=product['system_code'],
            order_number=referral_number,
            qty=product['count'],
            sku=product['name'],
            type="export transfer",
            imeis=product['imeis'],
            oldQuantity=product_result['cardex_data'].get("old_quantity"),
            newQuantity=product_result['cardex_data'].get("new_quantity"),
            oldReserve=product_result['cardex_data'].get('old_reserve'),
            newRreserve=product_result['cardex_data'].get('new_reserve')
        )
        with MongoConnection() as client:
            client.cardex_collection.insert_one(cardex_detail)
        product_result.pop("cardex_data")
        return product_result
    else:
        return product_result


def import_transfer_form(product, dst_warehouse, referral_number):
    product_result = addRemoveQuantity.add_quantity(product['system_code'], dst_warehouse, product['count'],
                                                    product['customer_type'], product['sell_price'])
    # TODO imeis
    if product_result.get("success"):
        cardex_detail = cardex(
            storage_id=dst_warehouse,
            system_code=product['system_code'],
            order_number=referral_number,
            qty=product['count'],
            sku=product['name'],
            type="import transfer",
            imeis=product['imeis'],
            oldQuantity=product_result['cardex_data'].get("old_quantity"),
            newQuantity=product_result['cardex_data'].get("new_quantity"),
            oldReserve=product_result['cardex_data'].get('reserve'),
            newRreserve=product_result['cardex_data'].get('reserve')
        )
        with MongoConnection() as client:
            client.cardex_collection.insert_one(cardex_detail)
        product_result.pop("cardex_data")
        return product_result
    else:
        return product_result


def all_warehouses():
    return warehouses()


def warehouse(storage_id):
    return find_warehouse(storage_id)
