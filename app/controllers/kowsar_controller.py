from app.models.kowsar import KowsarPart, KowsarGroup, KowsarConfig
from app.modules.kowsar_getter import KowsarGetter


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
    For the root category use "00"
    """
    data = KowsarGetter.system_code_items_getter(system_code)
    if data:
        return {"success": True, "message": data, "status_code": 200}
    return {"success": False, "error": "کالای مورد نظر یافت نشد", "status_code": 404}


def create_system_code(system_code, storage_ids, parent_system_code, guaranty):
    """
    create system code from model code
    """
    kowsar = KowsarPart(system_code, storage_ids, parent_system_code, guaranty)
    if not kowsar.is_unique():
        return {"success": False, "error": "کد مورد نظر قبلا ساخته شده است", "status_code": 400}
    data = KowsarGetter.system_code_name_getter(parent_system_code)
    if not data:
        return {"success": False, "status_code": 404, "error": "کالای مورد نظر یافت نشد"}
    # name = kowsar.name_getter()
    # name = data.get("brand", "").upper() + " " + data.get("model", "").upper() + " " + name.upper()
    # result, system_code = kowsar.create_kowsar_part(name, storage_ids, system_code)
    result = True
    if result:
        kowsar.create_in_db(data)
        return {"success": True, "message": {
            "system_code": system_code,
            "message": "با موفقیت ایجاد شد"
        }, "status_code": 200}
    return {"success": False, "error": "ساخت محصول با خطا مواجه شد", "status_code": 500}


def create_kowsar_group(system_code, name, parent_system_code, configs):
    """
    create kowsar group
    """
    kowsar = KowsarGroup(system_code, name, parent_system_code, configs)
    if not kowsar.is_unique():
        return {"success": False, "error": "گروه مورد نظر قبلا ساخته شده است", "status_code": 400}
    parent_data = None
    if len(system_code) != 2:
        parent_data = KowsarGetter.system_code_name_getter(parent_system_code)
    # result = kowsar.create_kowsar_group(parent_data)
    result = True
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


def create_kowsar_static_configs(config_type, system_code, name):
    """
    create kowsar static configs
    """
    if KowsarConfig.is_unique(config_type, system_code):
        result = KowsarConfig.create_static_configs(config_type, system_code, name)
        if result:
            return {"success": True, "message": "با موفقیت ایجاد شد", "status_code": 200}
        return {"success": False, "error": "ساخت گروه با خطا مواجه شد", "status_code": 500}
    return {"success": False, "error": "گروه مورد نظر قبلا ساخته شده است", "status_code": 400}


def get_kowsar_static_configs_by_config_type(config_type):
    """
    get kowsar static configs by config type
    """
    data = KowsarConfig.get_static_configs_by_config_type(config_type)
    if data:
        return {"success": True, "message": data, "status_code": 200}
    return {"success": False, "error": "گروه مورد نظر یافت نشد", "status_code": 404}
