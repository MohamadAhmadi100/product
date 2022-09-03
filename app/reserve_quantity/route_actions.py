from app.reserve_quantity.add_remove_model import AddRemoveQtyReserve
from app.reserve_quantity.cardex import cardex
from app.reserve_quantity.imeis import *


class ReserveRoutes:
    def __init__(self, order):
        self.order: dict = order
        self.add_remove_reserve = AddRemoveQtyReserve()

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
                    "order_number": self.order['orderNumber']
                }
                provided_data.append(product_detail)
        return provided_data

    def add_to_reserve_order(self, system_code, storage_id, count, customer_type, sku, order_number):
        """
        order add to reserve
        """
        reserve_result = self.add_remove_reserve.add_reserve(system_code, storage_id, count, customer_type,
                                                             order_number)
        if reserve_result.get("success"):
            quantity_cardex_data = cardex(
                storage_id=storage_id,
                system_code=system_code,
                incremental_id=order_number,
                qty=count,
                sku=sku,
                type="new cart",
                oldQuantity=reserve_result['cardex'].get('oldQuantity'),
                newQuantity=reserve_result['cardex'].get('newQuantity'),
                oldReserve=reserve_result['cardex'].get('oldReserve'),
                newRreserve=reserve_result['cardex'].get('newRreserve')
            )
            reserve_result['quantity_cardex_data'] = quantity_cardex_data
            return reserve_result
        else:
            return {"success": False, "error": f"{system_code}"}

    def add_to_reserve_dealership(self, system_code, storage_id, count, customer_type, sku, order_number):
        """
        dealership add to reserve
        """
        reserve_result = self.add_remove_reserve.add_reserve(system_code, storage_id, count, customer_type,
                                                             order_number)
        if reserve_result.get("success"):
            quantity_cardex_data = cardex(
                storage_id=storage_id,
                system_code=system_code,
                incremental_id=order_number,
                qty=count,
                sku=sku,
                type="dealership",
                oldQuantity=reserve_result['cardex'].get('oldQuantity'),
                newQuantity=reserve_result['cardex'].get('newQuantity'),
                oldReserve=reserve_result['cardex'].get('oldReserve'),
                newReserve=reserve_result['cardex'].get('newReserve')
            )
            reserve_result['quantity_cardex_data'] = quantity_cardex_data
            return reserve_result
        else:
            return {"success": False, "error": f"{system_code}"}

    def remove_reserve_cancel(self, system_code, storage_id, count, customer_type, sku, order_number):
        """
        cancel order remove reserve
        """
        reserve_result = self.add_remove_reserve.remove_reserve(system_code, storage_id, count, customer_type,
                                                                order_number)
        if reserve_result.get("success"):
            quantity_cardex_data = cardex(
                storage_id=storage_id,
                system_code=system_code,
                incremental_id=order_number,
                qty=count,
                sku=sku,
                type="cancel orders",
                oldQuantity=reserve_result['cardex'].get('oldQuantity'),
                newQuantity=reserve_result['cardex'].get('newQuantity'),
                oldReserve=reserve_result['cardex'].get('oldReserve'),
                newReserve=reserve_result['cardex'].get('newReserve')
            )
            reserve_result['quantity_cardex_data'] = quantity_cardex_data
            return reserve_result
        else:
            return {"success": False, "error": f"{system_code}"}

    def remove_reserve_rollback(self, system_code, storage_id, count, customer_type, sku, order_number):
        """
        rollback remove reserve
        """
        reserve_result = AddRemoveQtyReserve.remove_reserve(system_code, storage_id, count, customer_type,
                                                            order_number)
        if reserve_result.get("success"):
            return reserve_result
        else:
            return {"success": False, "error": f"{system_code}"}

    def add_reserve_rollback(self, system_code, storage_id, count, customer_type, sku, order_number):
        """
        order add to reserve
        """
        reserve_result = AddRemoveQtyReserve.add_reserve(system_code, storage_id, count, customer_type,
                                                         order_number)
        if reserve_result.get("success"):
            return reserve_result
        else:
            return {"success": False, "error": f"{system_code}"}

    def remove_reserve_edit_order(self, system_code, storage_id, count, customer_type, sku, order_number):
        """
        remove reserve edit order
        """
        reserve_result = AddRemoveQtyReserve.remove_reserve(system_code, storage_id, count, customer_type,
                                                            order_number)
        if reserve_result.get("success"):
            quantity_cardex_data = cardex(
                storage_id=storage_id,
                system_code=system_code,
                incremental_id=order_number,
                qty=count,
                sku=sku,
                type="edit orders",
                oldQuantity=reserve_result['cardex'].get('oldQuantity'),
                newQuantity=reserve_result['cardex'].get('newQuantity'),
                oldReserve=reserve_result['cardex'].get('oldReserve'),
                newReserve=reserve_result['cardex'].get('newReserve')
            )
            reserve_result['quantity_cardex_data'] = quantity_cardex_data
            return reserve_result
        else:
            return {"success": False, "error": f"{system_code}"}

    def export_transfer_form(self, product, src_warehouse, dst_warehouse, referral_number, customer_type):
        """
        export transfer remove reserve and quantity
        """
        reserve_result = AddRemoveQtyReserve.remove_reserve_quantity(product['system_code'],
                                                                     src_warehouse['storage_id'],
                                                                     product['count'], customer_type)
        if reserve_result.get("success"):
            export_transfer_archive(product, dst_warehouse, referral_number, "staff_name")
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
                old_reserve=reserve_result['cardex'].get('oldReserve'),
                new_reserve=reserve_result['cardex'].get('newReserve')
            )
            reserve_result['quantity_cardex_data'] = quantity_cardex_data
            return reserve_result
        else:
            return {"success": False, "error": f"{product['system_code']}"}

    def import_transfer_form(self, product, src_warehouse, dst_warehouse, referral_number, quantity_type, staff_name):
        reserve_result = AddRemoveQtyReserve.add_quantity(product['system_code'], src_warehouse['storage_id'],
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
                old_reserve=reserve_result['cardex'].get('oldReserve'),
                new_reserve=reserve_result['cardex'].get('newReserve')
            )
            reserve_result['quantity_cardex_data'] = quantity_cardex_data
            return reserve_result
        else:
            return {"success": False, "error": f"{product['system_code']}"}

    def create_transfer_reserve(self, product, src_warehouse, dst_warehouse, referral_number, quantity_type,
                                staff_name):
        reserve_result = AddRemoveQtyReserve.add_reserve(product['system_code'], src_warehouse['storage_id'],
                                                         product['count'], quantity_type, referral_number)

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
                old_reserve=reserve_result['cardex'].get('oldReserve'),
                new_reserve=reserve_result['cardex'].get('newReserve')
            )
            reserve_result['quantity_cardex_data'] = quantity_cardex_data
            return reserve_result
        else:
            return {"success": False, "error": f"{product['system_code']}"}

    def add_buying_form(self, product, dst_warehouse, customer_type, referral_number, supplier_name, form_date):
        reserve_result = AddRemoveQtyReserve.add_quantity(product['system_code'], dst_warehouse['storage_id'],
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
                    type="import transfer",
                    imeis=product['imeis'],
                    old_quantity=reserve_result['cardex'].get('oldQuantity'),
                    new_quantity=reserve_result['cardex'].get('newQuantity'),
                    old_reserve=reserve_result['cardex'].get('oldReserve'),
                    new_reserve=reserve_result['cardex'].get('newReserve')
                )
                with MongoConnection() as client:
                    client.cardex_collection.insert_one(quantity_cardex_data)
                reserve_result.pop("cardex")
                return reserve_result
        else:
            return {"success": False, "error": f"{product['system_code']}"}
