from app.reserve_quantity.add_remove_model import AddRemoveQtyReserve
from app.reserve_quantity.cardex import cardex
from app.reserve_quantity.imeis import *


class OrderModel:
    def __init__(self, order):
        self.order: dict = order

    @property
    def order_data(self):
        provided_data = []
        customer_type = self.order["customer"]["type"]
        for item in self.order["splitedOrder"]:
            storage_id = item["storageId"]
            for product in item["products"]:
                product_detail = {
                    "system_code": product["systemCode"],
                    "storage_id": storage_id,
                    "count": product["count"],
                    "customer_type": customer_type,
                    "sku": product["name"],
                    "order_number": self.order['orderNumber'],
                    "imei": product.get("imeis")
                }
                provided_data.append(product_detail)
        return provided_data

    @property
    def return_order_data(self):
        provided_data = []
        customer_type = self.order["customer"]["type"]
        return_log = self.order["logs"].get('returnLog')
        returned_imeis = []
        if return_log is not None:
            for cursor in return_log:
                returned_imeis.append(cursor['imei'])
        for item in self.order["splitedOrder"]:
            storage_id = item["storageId"]
            for product in item["products"]:
                for imeis in product['imeis']:
                    if imeis not in returned_imeis:
                        product_detail = {
                            "system_code": product["systemCode"],
                            "storage_id": storage_id,
                            "count": 1,
                            "customer_type": customer_type,
                            "sku": product["name"],
                            "order_number": self.order['orderNumber'],
                            "imei": imeis
                        }
                        provided_data.append(product_detail)
        return provided_data


def add_to_reserve_order(system_code, storage_id, count, customer_type, sku, order_number):
    """
    order add to reserve
    """
    add_remove_model = AddRemoveQtyReserve()
    reserve_result = add_remove_model.add_reserve(system_code, storage_id, count, customer_type,
                                                  order_number)
    if reserve_result.get("success"):
        quantity_cardex_data = cardex(
            storage_id=storage_id,
            system_code=system_code,
            incremental_id=order_number,
            qty=count,
            sku=sku,
            type="new cart",
            old_quantity=reserve_result['cardex'].get('oldQuantity'),
            new_quantity=reserve_result['cardex'].get('newQuantity'),
            old_inventory=reserve_result['cardex'].get('oldInventory'),
            new_inventory=reserve_result['cardex'].get('newInventory'),
            old_reserve=reserve_result['cardex'].get('oldReserve'),
            new_reserve=reserve_result['cardex'].get('newReserve')
        )
        reserve_result['quantity_cardex_data'] = quantity_cardex_data
        return reserve_result
    else:
        return {"success": False, "error": f"{system_code}"}


def add_to_reserves_reorder(system_code, storage_id, count, customer_type, sku, order_number, staff_name):
    """
    order add to reserve
    """
    add_remove_model = AddRemoveQtyReserve()
    reserve_result = add_remove_model.add_reserve(system_code, storage_id, count, customer_type,
                                                  order_number)
    if reserve_result.get("success"):
        quantity_cardex_data = cardex(
            storage_id=storage_id,
            system_code=system_code,
            incremental_id=order_number,
            qty=count,
            sku=sku,
            type="reorder",
            old_quantity=reserve_result['cardex'].get('oldQuantity'),
            new_quantity=reserve_result['cardex'].get('newQuantity'),
            old_inventory=reserve_result['cardex'].get('oldInventory'),
            new_inventory=reserve_result['cardex'].get('newInventory'),
            old_reserve=reserve_result['cardex'].get('oldReserve'),
            new_reserve=reserve_result['cardex'].get('newReserve'),
            user=staff_name
        )
        reserve_result['quantity_cardex_data'] = quantity_cardex_data
        return reserve_result
    else:
        return {"success": False, "error": f"{system_code}"}


def add_to_reserves_dealership(system_code, storage_id, count, customer_type, sku, order_number):
    """
    dealership add to reserve
    """
    add_remove_model = AddRemoveQtyReserve()
    reserve_result = add_remove_model.add_reserve(system_code, storage_id, count, customer_type,
                                                  order_number)
    if reserve_result.get("success"):
        quantity_cardex_data = cardex(
            storage_id=storage_id,
            system_code=system_code,
            incremental_id=order_number,
            qty=count,
            sku=sku,
            type="dealership reserve",
            old_quantity=reserve_result['cardex'].get('oldQuantity'),
            new_quantity=reserve_result['cardex'].get('newQuantity'),
            old_inventory=reserve_result['cardex'].get('oldInventory'),
            new_inventory=reserve_result['cardex'].get('newInventory'),
            old_reserve=reserve_result['cardex'].get('oldReserve'),
            new_reserve=reserve_result['cardex'].get('newReserve')
        )
        reserve_result['quantity_cardex_data'] = quantity_cardex_data
        return reserve_result
    else:
        return {"success": False, "error": f"{system_code}"}


def remove_reserves_dealership(system_code, storage_id, count, customer_type, sku, order_number):
    """
    dealership add to reserve
    """
    add_remove_model = AddRemoveQtyReserve()
    reserve_result = add_remove_model.remove_reserve(system_code, storage_id, count, customer_type,
                                                     order_number)
    if reserve_result.get("success"):
        quantity_cardex_data = cardex(
            storage_id=storage_id,
            system_code=system_code,
            incremental_id=order_number,
            qty=count,
            sku=sku,
            type="dealership remove reserve",
            old_quantity=reserve_result['cardex'].get('oldQuantity'),
            new_quantity=reserve_result['cardex'].get('newQuantity'),
            old_inventory=reserve_result['cardex'].get('oldInventory'),
            new_inventory=reserve_result['cardex'].get('newInventory'),
            old_reserve=reserve_result['cardex'].get('oldReserve'),
            new_reserve=reserve_result['cardex'].get('newReserve')
        )
        reserve_result['quantity_cardex_data'] = quantity_cardex_data
        return reserve_result
    else:
        return {"success": False, "error": f"{system_code}"}


def remove_products_dealership_from_inv(system_code, imeis, dealership_detail, storage_id, count, customer_type, sku,
                                        referral_number):
    """
    dealership remove product from inv0
    """
    add_remove_model = AddRemoveQtyReserve()
    reserve_result = add_remove_model.remove_reserve_quantity(system_code, storage_id, count, customer_type,
                                                              )
    if reserve_result.get("success"):
        add_remove_model.add_quantity_dealership(system_code, 2000, count, customer_type,
                                                 )
        export_transfer_dealership(system_code, imeis, dealership_detail, referral_number)
        quantity_cardex_data = cardex(
            storage_id=storage_id,
            system_code=system_code,
            incremental_id=referral_number,
            qty=count,
            sku=sku,
            type="dealership transfer",
            old_quantity=reserve_result['cardex'].get('oldQuantity'),
            new_quantity=reserve_result['cardex'].get('newQuantity'),
            old_inventory=reserve_result['cardex'].get('oldInventory'),
            new_inventory=reserve_result['cardex'].get('newInventory'),
            old_reserve=reserve_result['cardex'].get('oldReserve'),
            new_reserve=reserve_result['cardex'].get('newReserve'),
            imeis=imeis
        )
        reserve_result['quantity_cardex_data'] = quantity_cardex_data
        return reserve_result
    else:
        return {"success": False, "error": f"{system_code}"}


def remove_reserve_cancel(system_code, storage_id, count, customer_type, sku, order_number):
    """
    cancel order remove reserve
    """
    add_remove_model = AddRemoveQtyReserve()
    reserve_result = add_remove_model.remove_reserve(system_code, storage_id, count, customer_type,
                                                     order_number)
    if reserve_result.get("success"):
        quantity_cardex_data = cardex(
            storage_id=storage_id,
            system_code=system_code,
            incremental_id=order_number,
            qty=count,
            sku=sku,
            type="cancel orders",
            old_quantity=reserve_result['cardex'].get('oldQuantity'),
            new_quantity=reserve_result['cardex'].get('newQuantity'),
            old_inventory=reserve_result['cardex'].get('oldInventory'),
            new_inventory=reserve_result['cardex'].get('newInventory'),
            old_reserve=reserve_result['cardex'].get('oldReserve'),
            new_reserve=reserve_result['cardex'].get('newReserve')
        )
        reserve_result['quantity_cardex_data'] = quantity_cardex_data
        return reserve_result
    else:
        return {"success": False, "error": f"{system_code}"}


def remove_reserve_rollback(system_code, storage_id, count, customer_type, order_number):
    """
    rollback remove reserve
    """
    add_remove_model = AddRemoveQtyReserve()
    reserve_result = add_remove_model.remove_reserve(system_code, storage_id, count, customer_type,
                                                     order_number)
    if reserve_result.get("success"):
        return reserve_result
    else:
        return {"success": False, "error": f"{system_code}"}


def add_reserve_rollback(system_code, storage_id, count, customer_type, order_number):
    """
    order add to reserve
    """
    add_remove_model = AddRemoveQtyReserve()
    reserve_result = add_remove_model.add_reserve(system_code, storage_id, count, customer_type,
                                                  order_number)
    if reserve_result.get("success"):
        return reserve_result
    else:
        return {"success": False, "error": f"{system_code}"}


def remove_reserve_edit_order(system_code, storage_id, count, customer_type, sku, order_number):
    """
    remove reserve edit order
    """
    add_remove_model = AddRemoveQtyReserve()
    reserve_result = add_remove_model.remove_reserve(system_code, storage_id, count, customer_type,
                                                     order_number)
    if reserve_result.get("success"):
        quantity_cardex_data = cardex(
            storage_id=storage_id,
            system_code=system_code,
            incremental_id=order_number,
            qty=count,
            sku=sku,
            type="edit orders",
            old_quantity=reserve_result['cardex'].get('oldQuantity'),
            new_quantity=reserve_result['cardex'].get('newQuantity'),
            old_inventory=reserve_result['cardex'].get('oldInventory'),
            new_inventory=reserve_result['cardex'].get('newInventory'),
            old_reserve=reserve_result['cardex'].get('oldReserve'),
            new_reserve=reserve_result['cardex'].get('newReserve')
        )
        reserve_result['quantity_cardex_data'] = quantity_cardex_data
        return reserve_result
    else:
        return {"success": False, "error": f"{system_code}"}


def export_transfer_form(product, src_warehouse, dst_warehouse, referral_number, customer_type, staff_name):
    """
    export transfer remove reserve and quantity
    """
    add_remove_model = AddRemoveQtyReserve()
    reserve_result = add_remove_model.remove_reserve_quantity(product['system_code'],
                                                              src_warehouse['storage_id'],
                                                              product['count'], customer_type)
    if reserve_result.get("success"):
        export_transfer_archive(product, dst_warehouse, referral_number, staff_name)
        quantity_cardex_data = cardex(
            storage_id=src_warehouse['storage_id'],
            system_code=product['system_code'],
            incremental_id=referral_number,
            qty=product['count'],
            sku=product['name'],
            type="export transfer",
            imeis=product['imeis'],
            old_quantity=reserve_result['cardex'].get('oldQuantity'),
            new_quantity=reserve_result['cardex'].get('newQuantity'),
            old_inventory=reserve_result['cardex'].get('oldInventory'),
            new_inventory=reserve_result['cardex'].get('newInventory'),
            old_reserve=reserve_result['cardex'].get('oldReserve'),
            new_reserve=reserve_result['cardex'].get('newReserve')
        )
        reserve_result['quantity_cardex_data'] = quantity_cardex_data
        return reserve_result
    else:
        return {"success": False, "error": f"{product['system_code']}"}


def import_transfer_form(product, src_warehouse, dst_warehouse, referral_number, quantity_type, staff_name):
    add_remove_model = AddRemoveQtyReserve()
    reserve_result = add_remove_model.add_quantity(product['system_code'], dst_warehouse['storage_id'],
                                                   product['count'],
                                                   quantity_type, product['sell_price'])

    if reserve_result.get("success"):
        import_transfer_archive(product, src_warehouse, dst_warehouse, referral_number, staff_name)
        quantity_cardex_data = cardex(
            storage_id=dst_warehouse,
            system_code=product['system_code'],
            incremental_id=referral_number,
            qty=product['count'],
            sku=product['name'],
            type="import transfer",
            imeis=product['imeis'],
            old_quantity=reserve_result['cardex'].get('oldQuantity'),
            new_quantity=reserve_result['cardex'].get('newQuantity'),
            old_inventory=reserve_result['cardex'].get('oldInventory'),
            new_inventory=reserve_result['cardex'].get('newInventory'),
            old_reserve=reserve_result['cardex'].get('oldReserve'),
            new_reserve=reserve_result['cardex'].get('newReserve')
        )
        reserve_result['quantity_cardex_data'] = quantity_cardex_data
        return reserve_result
    else:
        return {"success": False, "error": f"{product['system_code']}"}


def create_transfer_reserve(product, src_warehouse, dst_warehouse, referral_number, quantity_type,
                            staff_name):
    add_remove_model = AddRemoveQtyReserve()
    reserve_result = add_remove_model.add_reserve(product['system_code'], src_warehouse['storage_id'],
                                                  product['count'], quantity_type, referral_number)

    if reserve_result.get("success"):
        quantity_cardex_data = cardex(
            storage_id=dst_warehouse,
            system_code=product['system_code'],
            incremental_id=referral_number,
            qty=product['count'],
            sku=product['name'],
            type="create transfer",
            imeis=product['imeis'],
            old_quantity=reserve_result['cardex'].get('oldQuantity'),
            new_quantity=reserve_result['cardex'].get('newQuantity'),
            old_inventory=reserve_result['cardex'].get('oldInventory'),
            new_inventory=reserve_result['cardex'].get('newInventory'),
            old_reserve=reserve_result['cardex'].get('oldReserve'),
            new_reserve=reserve_result['cardex'].get('newReserve'),
            user=staff_name
        )
        reserve_result['quantity_cardex_data'] = quantity_cardex_data
        return reserve_result
    else:
        return {"success": False, "error": f"{product['system_code']}"}


def add_buying_form(product, dst_warehouse, customer_type, referral_number, supplier_name, form_date):
    add_remove_model = AddRemoveQtyReserve()
    reserve_result = add_remove_model.add_quantity(product['system_code'], dst_warehouse,
                                                   product['count'], customer_type, product['sell_price'])

    if reserve_result.get("success"):
        imei = add_imeis(product, dst_warehouse)
        archive = add_product_archive(product, referral_number, supplier_name, form_date, dst_warehouse)
        if imei and archive:
            quantity_cardex_data = cardex(
                storage_id=dst_warehouse,
                system_code=product['system_code'],
                incremental_id=referral_number,
                qty=product['count'],
                sku=product['name'],
                type="buying form",
                imeis=product['imeis'],
                old_quantity=reserve_result['cardex'].get('oldQuantity'),
                new_quantity=reserve_result['cardex'].get('newQuantity'),
                old_inventory=reserve_result['cardex'].get('oldInventory'),
                new_inventory=reserve_result['cardex'].get('newInventory'),
                old_reserve=reserve_result['cardex'].get('oldReserve'),
                new_reserve=reserve_result['cardex'].get('newReserve')
            )
            with MongoConnection() as client:
                client.cardex_collection.insert_one(quantity_cardex_data)
            reserve_result.pop("cardex")
            return reserve_result
    else:
        return {"success": False, "error": f"{product['system_code']}"}


def return_order_items(system_code, storage_id, customer_type, order_number, imei, staff_name):
    add_remove_model = AddRemoveQtyReserve()
    return_action = return_order(imei, system_code, storage_id)

    if return_action.get("success"):
        reserve_result = add_remove_model.add_quantity(system_code, storage_id,
                                                       1, customer_type, None)
        if reserve_result.get("success"):
            quantity_cardex_data = cardex(
                storage_id=storage_id,
                system_code=system_code,
                incremental_id=order_number,
                qty=1,
                sku=reserve_result['cardex'].get('name'),
                type="return order",
                imeis=imei,
                old_quantity=reserve_result['cardex'].get('oldQuantity'),
                new_quantity=reserve_result['cardex'].get('newQuantity'),
                old_inventory=reserve_result['cardex'].get('oldInventory'),
                new_inventory=reserve_result['cardex'].get('newInventory'),
                old_reserve=reserve_result['cardex'].get('oldReserve'),
                new_reserve=reserve_result['cardex'].get('newReserve'),
                user=staff_name
            )
            return_action['quantity_cardex_data'] = quantity_cardex_data
            return return_action
        else:
            return reserve_result
    else:
        return return_action


def remove_reserve_edit_transfer(system_code, storage_id, count, customer_type, order_number):
    """
    edit transfer form products
    """
    add_remove_model = AddRemoveQtyReserve()
    reserve_result = add_remove_model.remove_reserve(system_code, storage_id, count, customer_type,
                                                     order_number)
    if reserve_result.get("success"):
        quantity_cardex_data = cardex(
            storage_id=storage_id,
            system_code=system_code,
            incremental_id=order_number,
            qty=count,
            sku=reserve_result['cardex'].get('name'),
            type="edit transfer form",
            old_quantity=reserve_result['cardex'].get('oldQuantity'),
            new_quantity=reserve_result['cardex'].get('newQuantity'),
            old_inventory=reserve_result['cardex'].get('oldInventory'),
            new_inventory=reserve_result['cardex'].get('newInventory'),
            old_reserve=reserve_result['cardex'].get('oldReserve'),
            new_reserve=reserve_result['cardex'].get('newReserve')
        )
        reserve_result['quantity_cardex_data'] = quantity_cardex_data
        return reserve_result
    else:
        return {"success": False, "error": f"{system_code}"}


def add_to_reserve_edit_transfer(system_code, storage_id, count, customer_type, order_number):
    """
    edit transfer form products add to reserve
    """
    add_remove_model = AddRemoveQtyReserve()
    reserve_result = add_remove_model.add_reserve(system_code, storage_id, count, customer_type,
                                                  order_number)
    if reserve_result.get("success"):
        quantity_cardex_data = cardex(
            storage_id=storage_id,
            system_code=system_code,
            incremental_id=order_number,
            qty=count,
            sku=reserve_result['cardex'].get('name'),
            type="edit transfer form",
            old_quantity=reserve_result['cardex'].get('oldQuantity'),
            new_quantity=reserve_result['cardex'].get('newQuantity'),
            old_inventory=reserve_result['cardex'].get('oldInventory'),
            new_inventory=reserve_result['cardex'].get('newInventory'),
            old_reserve=reserve_result['cardex'].get('oldReserve'),
            new_reserve=reserve_result['cardex'].get('newReserve')
        )
        reserve_result['quantity_cardex_data'] = quantity_cardex_data
        return reserve_result
    else:
        return {"success": False, "error": f"{system_code}"}


def checking_reserve_to_dealership(
        storage_id: str,
        system_code: str,
        count: int,
        customer_type: str):
    try:
        with MongoConnection() as mongo:
            product = mongo.product.find_one({"system_code": system_code})
            if not product:
                return False, 0

            qty_object = product.get("warehouse_details", {}).get(customer_type, {}).get("storages", {}).get(storage_id,
                                                                                                             {})
            if not qty_object:
                return False, 0
            enable_count = qty_object["quantity"] - qty_object["reserved"]
            if enable_count < count:
                return False, enable_count
            return True, 1
    except Exception:
        return False, 0
