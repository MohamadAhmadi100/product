from app.models.product import CreateParent, Product
from app.models.product import CreateChild
from app.models.product import AddAtributes
from app.modules.attribute_setter import attribute_setter
from app.modules.kowsar_getter import KowsarGetter


def get_parent_configs(system_code: str):
    reslut = CreateParent.get_configs(system_code)
    if reslut:
        return {"success": True, "message": reslut, "status_code": 200}
    return {"success": False, "error": "parent configs not found", "status_code": 404}


def create_parent(system_code: str, name: str, visible_in_site: bool) -> dict:
    """
    Create a product for sale in main collection in database.
    attributes will be validated before insert.
    """
    parent = CreateParent(system_code, name, visible_in_site)
    if parent.system_code_is_unique():
        message, success = parent.create()
        if success:
            return {"success": True, "message": message, "status_code": 200}
        return {"success": False, "error": message, "status_code": 400}
    return {"success": False, "error": "system code is not unique", "status_code": 400}


def suggest_product(system_code: str):
    data = KowsarGetter.system_code_items_getter(system_code[:9])
    parents_data = KowsarGetter.get_parents(system_code)
    if parents_data:
        config = (parents_data.get("attributes").get("storage"), parents_data.get("attributes").get("ram"))
        suggests = CreateChild.suggester(data, system_code, config)
        return {"success": True, "message": suggests, "status_code": 200}
    return {"success": False, "error": "parent configs not found", "status_code": 404}


def create_child(system_code: str, parent_system_code: str, visible_in_site: bool) -> dict:
    """
    Create a product for sale in main collection in database.
    attributes will be validated before insert.
    """
    child = CreateChild(system_code, parent_system_code, visible_in_site)
    if child.system_code_is_unique():
        message, success = child.create()
        if success:
            return {"success": True, "message": message, "status_code": 201}
        return {"success": False, "error": message, "status_code": 400}
    return {"success": False, "error": "child system code is not unique", "status_code": 400}


def add_attributes(system_code: str, attributes: dict) -> dict:
    """
    Create a product for sale in main collection in database.
    attributes will be validated before insert.
    """
    attributes = AddAtributes(system_code, attributes)
    if not attributes.system_code_is_unique():
        message, success = attributes.create()
        if success:
            return {"success": True, "message": message, "status_code": 201}
        return {"success": False, "error": message, "status_code": 400}
    return {"success": False, "error": "system code not found", "status_code": 400}


def get_product_by_system_code(system_code: str, lang: str) -> dict:
    """
    Get a product by system_code in main collection in database.
    """
    result = Product.get_product_by_system_code(system_code, lang)
    if result:
        return {"success": True, "message": result, "status_code": 200}
    return {"success": False, "error": "product not found", "status_code": 404}


def delete_product(system_code: str) -> dict:
    """
    Delete a product by name in main collection in database.
    """
    child = CreateChild(system_code, "", False)
    if not child.system_code_is_unique():
        message, success = child.delete()
        if success:
            return {"success": True, "message": message, "status_code": 200}
        return {"success": False, "error": message, "status_code": 400}
    return {"success": False, "error": "product not found", "status_code": 404}


def update_attribute_collection(attributes: list) -> dict:
    """
    Update the attribute collection in database.
    """
    attribute_setter(attributes)
    return {"success": True, "message": {"message": "attribute collection updated"}, "status_code": 200}


def get_all_categories(system_code: str, page: int, per_page: int):
    """
    """
    result = Product.get_all_categories(system_code, page, per_page)
    if result:
        return {"success": True, "message": result, "status_code": 200}
    return {"success": False, "error": "categories not found", "status_code": 404}


def get_product_list(brand: str, page: int, per_page: int):
    """
    """
    result = Product.get_product_list(brand, page, per_page)
    if result:
        return {"success": True, "message": result, "status_code": 200}
    return {"success": False, "error": "products not found", "status_code": 404}


def get_category_list():
    """
    """
    result = Product.get_category_list()
    if result:
        return {"success": True, "message": result, "status_code": 200}
    return {"success": False, "error": "categories not found", "status_code": 404}


def get_product_list_back_office():
    """
    """
    result = Product.get_product_list_back_office()
    if result:
        return {"success": True, "message": result, "status_code": 200}
    return {"success": False, "error": "products not found", "status_code": 404}


def step_up_product(system_code: str):
    """
    """
    result = Product.step_up_product(system_code)
    if result:
        return {"success": True, "message": result, "status_code": 200}
    return {"success": False, "error": "product not found", "status_code": 404}
