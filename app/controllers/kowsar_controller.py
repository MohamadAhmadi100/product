from app.models.kowsar import KowsarGetter
from app.models.kowsar import KowsarPart, KowsarGroup


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


def create_system_code(system_code, storage_ids, guaranty):
    """
    create system code from model code
    """
    parent_system_code = system_code[:22]
    kowsar = KowsarPart(system_code, storage_ids, parent_system_code, guaranty)
    if not kowsar.is_unique():
        return {"success": False, "error": "کد مورد نظر قبلا ساخته شده است", "status_code": 400}
    data = KowsarGetter.system_code_name_getter(parent_system_code)
    if not data:
        return {"success": False, "status_code": 404, "error": "کالای مورد نظر یافت نشد"}

    configs = data.get("configs")

    name = data['sub_category'] + " " + data['brand'] + " " + data['model']

    if data.get('sub_category') in ["Mobile", "Tablet"]:
        name += ' (' + configs['ram'] + ' ' + configs['storage'] + ' ' + configs[
            'network'] + ") " + configs['region'] + " | " + data[
                    'seller'] + " | " + guaranty + " " + f"[{data['color']}]"
    else:
        name += ' (' + " ".join([v for k, v in configs.items() if v]) + ') ' + data[
            'seller'] + " | " + guaranty + " " + f"[{data['color']}]"

    result, response = kowsar.create_kowsar_part(name, storage_ids, system_code)
    kowsar.log(response, result)
    if result:
        if kowsar.create_in_db(data, name):
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
        if not parent_data:
            return {"success": False, "error": "پرنت محصول یافت نشد", "status_code": 404}
    if len(system_code) == 16 and configs:
        if parent_data.get('sub_category') in ["Mobile", "Tablet"]:
            kowsar.name = parent_data['model'] + ' (' + configs['ram'] + ' ' + configs['storage'] + ' ' + configs[
                'network'] + ") " + configs['region']
        else:
            kowsar.name = parent_data['model'] + ' (' + " ".join([v for k, v in configs.items() if v]) + ')'
    result = True
    response = None
    if len(system_code) <= 16:
        result, response = kowsar.create_kowsar_group(parent_data)
    kowsar.log(response, result)
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


def get_kowsar_system_code(system_code):
    result = KowsarGetter.get_kowsar_system_code(system_code)
    if result:
        return {"success": True, "message": result, "status_code": 200}
    return {"success": False, "error": "product not found", "status_code": 500}


def assign_system_code_to_seller(system_codes: dict, seller: str, seller_code: str):
    for system_code in system_codes:
        storage_ids = system_code.get("storage_ids")
        system_code = system_code.get("system_code")
        parent_data = KowsarGetter.system_code_name_getter(system_code)
        seller_group = create_kowsar_group(system_code[:16] + seller_code, seller, system_code[:16], None)
        color_group = create_kowsar_group(system_code[:16] + seller_code + system_code[19:22], parent_data.get("color"),
                                          system_code[:16] + seller_code, None)

        system_code_part = create_system_code(system_code[:16] + seller_code + system_code[19:], storage_ids,
                                              parent_data.get("guaranty"))

    return {"success": True, "message": {"message": "با موفقیت ایجاد شد"}, "status_code": 200}


def get_kowsar_logs():
    result = KowsarGetter.get_kowsar_logs()
    if result:
        return {"success": True, "message": result, "status_code": 200}
    return {"success": False, "error": "product not found", "status_code": 500}


def kowsar_redo(func_name, request):
    response = globals().get(func_name)(**request)
    return response
