from app.models.kowsar import KowsarPart, KowsarGroup
from app.modules.kowsar_getter import KowsarGetter
from app.modules.translator import update_redis_database


def get_kowsar(system_code: str):
    """
    Get kowsar data by full system_code(12 digits)
    """
    data = KowsarGetter.system_code_name_getter(system_code)
    if data:
        return {"success": True, "message": data, "status_code": 200}
    return {"success": False, "status_code": 404, "error": "کالای مورد نظر یافت نشد"}


def get_kowsar_items(system_code: str):
    """
    Get sub categories of kowsar tree(2 to 9 digits)
    For the root category use "00"
    """
    data = KowsarGetter.system_code_items_getter(system_code)
    if data:
        return {"success": True, "message": data, "status_code": 200}
    return {"success": False, "error": "کالای مورد نظر یافت نشد", "status_code": 404}


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


def create_system_code(model_code, config, storage_ids):
    """
    create system code from model code
    """
    kowsar = KowsarPart(model_code, config)
    data = KowsarGetter.system_code_name_getter(model_code)
    if not data:
        return {"success": False, "status_code": 404, "error": "کالای مورد نظر یافت نشد"}
    name = kowsar.name_getter()
    name = data.get("brand", "").upper() + " " + data.get("model", "").upper() + " " + name.upper()
    system_code = kowsar.system_code_getter(model_code)
    result, system_code = kowsar.create_kowsar_part(name, storage_ids, model_code + system_code)
    if result:
        kowsar.create_in_db(data, system_code)
        return {"success": True, "message": {
            "system_code": system_code,
            "message": "با موفقیت ایجاد شد"
        }, "status_code": 200}
    return {"success": False, "error": "ساخت محصول با خطا مواجه شد", "status_code": 500}


def create_kowsar_group(system_code, name, parent_system_code):
    """
    create kowsar group
    """
    kowsar = KowsarGroup(system_code, name, parent_system_code)
    if not kowsar.is_unique():
        return {"success": False, "error": "گروه مورد نظر قبلا ساخته شده است", "status_code": 400}
    parent_data = KowsarGetter.system_code_name_getter(parent_system_code)
    result = kowsar.create_kowsar_group(parent_data)
    if result:
        complete_data = kowsar.category_name_getter(parent_data)
        mongo_result = kowsar.create_in_db(complete_data)
        if not mongo_result:
            return {"success": False, "error": "ساخت گروه در دیتابیس با خطا مواجه شد", "status_code": 500}
        return {"success": True, "message": {
            "system_code": system_code,
            "message": "با موفقیت ایجاد شد"
        }, "status_code": 200}
    return {"success": False, "error": "ساخت گروه با خطا مواجه شد", "status_code": 500}
