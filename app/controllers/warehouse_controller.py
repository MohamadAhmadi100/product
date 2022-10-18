from app.helpers.warehouses import *


def all_warehouses():
    return warehouses()


def warehouse(storage_id):
    return find_warehouse(storage_id)

