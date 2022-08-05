from app.reserve_quantity.add_remove_model import AddRemoveReserve
from app.reserve_quantity.cardex import cardex


def add_reserve_msm_order(system_code, storage_id, count, order_number):
    reserve = AddRemoveReserve.add_reserve_msm(system_code, storage_id, count, order_number)
    if reserve.get("success"):
        msm_cardex_data = cardex(
            storage_id=storage_id,
            system_code=system_code,
            order_number=order_number,
            qty=count,
            sku=reserve['product'].get("sku"),
            type="new cart",
            oldQuantity=reserve['product'].get("quantity"),
            newQuantity=reserve['product'].get("quantity"),
            oldReserve=reserve['product'].get("reserve"),
            newRreserve=int(reserve.get('product', {}).get("reserve", 0)) + count
        )
        reserve["msm_cardex_data"] = msm_cardex_data
        return reserve


def add_reserve_quantity_order(system_code, storage_id, count, customer_type, sku, order_number):
    reserve = AddRemoveReserve.add_reserve_quantity(system_code, storage_id, count, customer_type, order_number)
    # cardex
    if reserve.get("success"):
        quantity_cardex_data = cardex(
            storage_id=storage_id,
            system_code=system_code,
            order_number=order_number,
            qty=count,
            sku=sku,
            type="new cart",
            oldQuantity=reserve['product'].get("quantity"),
            newQuantity=reserve['product'].get("quantity"),
            oldReserve=int(reserve['product'].get('reserved')) - count,
            newRreserve=reserve['product'].get('reserved')
        )
        reserve['quantity_cardex_data'] = quantity_cardex_data
        return reserve
    else:
        return reserve


def dealership_add_reserve_quantity(system_code, storage_id, count, customer_type, sku, order_number):
    reserve = AddRemoveReserve.add_reserve_quantity(system_code, storage_id, count, customer_type, order_number)
    # cardex
    if reserve.get("success"):
        quantity_cardex_data = cardex(
            storage_id=storage_id,
            system_code=system_code,
            order_number=order_number,
            qty=count,
            sku=sku,
            type="dealership",
            oldQuantity=reserve['product'].get("quantity"),
            newQuantity=reserve['product'].get("quantity"),
            oldReserve=reserve['product'].get('reserved') - count,
            newRreserve=reserve['product'].get('reserved')
        )
        reserve['quantity_cardex_data'] = quantity_cardex_data
        return reserve
    else:
        return reserve


def dealership_add_reserve_msm(system_code, storage_id, count, order_number):
    reserve = AddRemoveReserve.add_reserve_msm(system_code, storage_id, count, order_number)
    if reserve.get("success"):
        msm_cardex_data = cardex(
            storage_id=storage_id,
            system_code=system_code,
            order_number=order_number,
            qty=count,
            sku=reserve['product'].get("sku"),
            type="dealership",
            oldQuantity=reserve['product'].get("quantity"),
            newQuantity=reserve['product'].get("quantity"),
            oldReserve=reserve['product'].get("reserve") - count,
            newRreserve=int(reserve['product'].get("reserve"))
        )
        reserve["msm_cardex_data"] = msm_cardex_data
        return reserve
    else:
        return reserve


def remove_from_msm_cancel_order(system_code, storage_id, count, order_number):
    reserve = AddRemoveReserve.remove_reserve_msm(system_code, storage_id, count, order_number)
    if reserve.get("success"):
        msm_cardex_data = cardex(
            storage_id=storage_id,
            system_code=system_code,
            order_number=order_number,
            qty=count,
            sku=reserve['product'].get("sku"),
            type="cancel orders",
            oldQuantity=reserve['product'].get("quantity"),
            newQuantity=reserve['product'].get("quantity"),
            oldReserve=reserve['product'].get("reserve"),
            newRreserve=int(reserve['product'].get("reserve")) + count
        )
        reserve["msm_cardex_data"] = msm_cardex_data
        return reserve
    else:
        return reserve


def remove_from_quantity_cancel_order(system_code, storage_id, count, customer_type, sku, order_number):
    reserve = AddRemoveReserve.remove_reserve_quantity(system_code, storage_id, count, customer_type, order_number)
    # cardex
    if reserve.get("success"):
        quantity_cardex_data = cardex(
            storage_id=storage_id,
            system_code=system_code,
            order_number=order_number,
            qty=count,
            sku=sku,
            type="cancel orders",
            oldQuantity=reserve['product'].get("quantity"),
            newQuantity=reserve['product'].get("quantity"),
            oldReserve=reserve['product'].get('reserved'),
            newRreserve=int(reserve['product'].get('reserved')) + count
        )
        reserve['quantity_cardex_data'] = quantity_cardex_data
        return reserve
    else:
        return reserve


def remove_msm_edit_order(system_code, storage_id, count, order_number):
    reserve = AddRemoveReserve.remove_reserve_msm(system_code, storage_id, count, order_number)
    if reserve.get("success"):
        msm_cardex_data = cardex(
            storage_id=storage_id,
            system_code=system_code,
            order_number=order_number,
            qty=count,
            sku=reserve['product'].get("sku"),
            type="edit orders",
            oldQuantity=reserve['product'].get("quantity"),
            newQuantity=reserve['product'].get("quantity"),
            oldReserve=reserve['product'].get("reserve"),
            newRreserve=int(reserve['product'].get("reserve")) + count
        )
        reserve["msm_cardex_data"] = msm_cardex_data
        return reserve
    else:
        return reserve


def remove_quantity_edit_order(system_code, storage_id, count, customer_type, sku, order_number):
    reserve = AddRemoveReserve.remove_reserve_quantity(system_code, storage_id, count, customer_type, order_number)
    # cardex
    if reserve.get("success"):
        quantity_cardex_data = cardex(
            storage_id=storage_id,
            system_code=system_code,
            order_number=order_number,
            qty=count,
            sku=sku,
            type="cancel orders",
            oldQuantity=reserve['product'].get("quantity"),
            newQuantity=reserve['product'].get("quantity"),
            oldReserve=reserve['product'].get('reserved'),
            newRreserve=int(reserve['product'].get('reserved')) + count
        )
        reserve['quantity_cardex_data'] = quantity_cardex_data
        return reserve
    else:
        return reserve
