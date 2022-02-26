from app.modules.kowsar_getter import KowsarGetter
from app.modules.translator import update_redis_database


def get_kowsar(system_code: str):
    """
    Get kowsar data by full system_code(12 digits)
    """
    data = KowsarGetter.system_code_name_getter(system_code)
    if data:
        return {"success": True, "message": data, "status_code": 200}
    return {"success": False, "status_code": 400, "message": "کالای مورد نظر یافت نشد"}


def get_kowsar_items(system_code: str):
    """
    Get sub categories of kowsar tree(2 to 9 digits)
    For the root category use "00"
    """
    data = KowsarGetter.system_code_items_getter(system_code)
    if data:
        return {"success": True, "message": data, "status_code": 200}
    return {"success": False, "message": "کالای مورد نظر یافت نشد", "status_code": 400}


def update_kowsar_collection():
    """
    update kowsar collection from kala file(.xls)
    """
    kowsar = KowsarGetter()
    kowsar.product_getter()
    kowsar.update_kowsar_collection()
    KowsarGetter.create_new_parents()
    update_redis_database()
    return {"success": True, "message": "با موفقیت به روز رسانی شد", "status_code": 200}
