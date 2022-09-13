from app.models.scm_quantity import *


def inv_initial_report(quantity_type):
    try:
        return initial_inv_report(quantity_type)
    except:
        return {'success': False, 'error': 'root exception error', 'status_code': 400}


def inv_products_report(storages, system_code, name, daily_system_code, daily_result):
    try:
        return inv_report(storages, system_code, name, daily_system_code, daily_result)
    except:
        return {'success': False, 'error': 'root exception error', 'status_code': 400}

