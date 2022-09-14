from app.models.product import Product, AddAttributes, Price, Quantity
from app.modules import csv_getter


def create_product(name, url_name, system_codes):
    """
    Create a product for sale in main collection in database.
    attributes will be validated before insert.
    """
    product = Product(name, url_name, system_codes)
    if product.system_codes_are_unique():
        result = product.make_product_obj()
        if not result:
            return {"success": False, "error": "system codes are not found in kowsar", "status_code": 400}
        success = product.create()
        if success:
            return {"success": True, "message": "products created successfully", "status_code": 201}
        return {"success": False, "error": "products did not created successfully", "status_code": 400}
    return {"success": False, "error": "system codes are not unique", "status_code": 400}


def get_product_attributes(system_code: str) -> dict:
    """
    Get a product by system_code in main collection in database.
    """
    message, result = Product.get_product_attributes(system_code)
    if result:
        return {"success": True, "message": message, "status_code": 200}
    return {"success": False, "error": message, "status_code": 404}


def add_attributes(system_code: str, attributes: dict) -> dict:
    """
    Create a product for sale in main collection in database.
    attributes will be validated before insert.
    """
    attributes = AddAttributes(system_code, attributes)
    if attributes.system_code_exists():
        message, success = attributes.create()
        if success:
            return {"success": True, "message": message, "status_code": 201}
        return {"success": False, "error": message, "status_code": 400}
    return {"success": False, "error": "system code not found", "status_code": 400}


def get_product_backoffice(system_code: str):
    """
    """
    result = Product.get_product_backoffice(system_code)
    if result:
        return {"success": True, "message": result, "status_code": 200}
    return {"success": False, "error": "product not found", "status_code": 404}


def set_product_price(system_code: str, customer_type: dict):
    price = Price(system_code, customer_type)
    if price.system_code_exists():
        result = price.set_product_price()
        if result:
            return {"success": True, "message": "price updated successfully", "status_code": 201}
    return {"success": False, "error": "product not found", "status_code": 404}


def update_price(system_code: str, customer_type: str, storage_id: str, regular: int, special: int,
                 informal_price: dict,
                 special_from_date: str,
                 special_to_date: str) -> dict:
    """
    update price (regular & special) by customer type and storage for a system code
    """
    data = Price.update_price(system_code, customer_type, storage_id, regular, special, informal_price,
                              special_from_date, special_to_date)
    if data:
        return {"success": True, "status_code": 202, "message": data}
    return {"success": False, "status_code": 417, "error": "failed to update price"}


def get_stock(system_code: str) -> dict:
    """
    get stock of a system_code
    """
    result = Quantity.get_stock(system_code)
    if result['total'] == 0:
        return {"success": False, "status_code": 404, "error": Quantity.get_all_stocks()}
    return {"success": True, "status_code": 200, "message": result}


def set_product_quantity(system_code, customer_types) -> dict:
    """
    set quantity per stock and user type
    """
    quantity = Quantity(system_code, customer_types)
    result = quantity.set_quantity()
    if result:
        return {"success": True, "status_code": 201, "message": "Quantity updated successfully"}
    return {"success": False, "status_code": 417, "error": "Error while setting quantity"}


def update_quantity(system_code: str, customer_type: str, storage_id: str, quantity: int,
                    min_qty: int, max_qty: int) -> dict:
    """
    update quantity of a system_code
    """
    result = Quantity.update_quantity(system_code, customer_type, storage_id, quantity, min_qty, max_qty)
    if result:
        return {"success": True, "status_code": 200, "message": result}
    return {"success": False, "status_code": 404, "error": "quantity not found"}


def get_product_list_back_office(brands: list, warehouses: list, price_from: int, price_to: int, sellers: list,
                                 colors: list, quantity_from: int, quantity_to: int, date_from: str, date_to: str,
                                 guarantees: list, steps: list, visible_in_site: bool, approved: bool, available: bool,
                                 page: int, per_page: int, lang: str) -> dict:
    """
    """
    result = Product.get_product_list_back_office(brands, warehouses, price_from, price_to, sellers, colors,
                                                  quantity_from, quantity_to, date_from, date_to, guarantees, steps,
                                                  visible_in_site, approved, available, page, per_page, lang)
    if result:
        return {"success": True, "message": result, "status_code": 200}
    return {"success": False, "error": "products not found", "status_code": 404}


def edit_product(system_code: str, item: dict) -> dict:
    """
    """
    if Product.system_code_exists(system_code):
        result = Product.edit_product(system_code, item)
        return {"success": True, "message": result, "status_code": 200}

    return {"success": False, "error": {"message": "product not found",
                                        "label": "محصول مورد نظر یافت نشد"}, "status_code": 404}


def get_product_by_system_code(system_code: str, lang: str) -> dict:
    """
    Get a product by system_code in main collection in database.
    """
    result = Product.get_product_by_system_code(system_code, lang)
    if result:
        return {"success": True, "message": result, "status_code": 200}
    return {"success": False, "error": "product not found", "status_code": 404}


def get_product_list_by_system_code(system_code, page, per_page, user_allowed_storages, customer_type):
    result = Product.get_product_list_by_system_code(system_code, page, per_page, user_allowed_storages, customer_type)
    if result:
        return {"success": True, "message": result, "status_code": 200}
    return {"success": False, "error": "product not found", "status_code": 404}


def get_product_page(system_code: str, user_allowed_storages: list, customer_type: str, lang: str) -> dict:
    """
    Get a product by system_code in main collection in database.
    """
    result = Product.get_product_page(system_code, user_allowed_storages, customer_type, lang)
    if result:
        return {"success": True, "message": result, "status_code": 200}
    return {"success": False, "error": "product not found", "status_code": 404}


def get_product_by_name(name: str, user_allowed_storages: list, customer_type: str):
    """
    """
    result = Product.get_product_by_name(name, user_allowed_storages, customer_type)
    if result:
        return {"success": True, "message": result, "status_code": 200}
    return {"success": False, "error": "product not found", "status_code": 404}


def get_category_list(user_allowed_storages: list, customer_type: str) -> dict:
    """
    Get a product by system_code in main collection in database.
    """
    result = Product.get_category_list(user_allowed_storages, customer_type)
    if result:
        return {"success": True, "message": result, "status_code": 200}
    return {"success": False, "error": "product not found", "status_code": 404}


def search_product_child(name: str, system_code: str, storages: list, customer_type: str) -> dict:
    """
    Get a product by system_code in main collection in database.
    """
    result = Product.search_product_child(name, system_code, storages, customer_type)
    if result:
        return {"success": True, "message": result, "status_code": 200}
    return {"success": False, "error": "product not found", "status_code": 404}


def get_csv(storage_id: str) -> dict:
    """
    Get a product by system_code in main collection in database.
    """
    result = csv_getter.get_csv(storage_id)
    if result:
        return {"success": True, "message": result, "status_code": 200}
    return {"success": False, "error": "product not found", "status_code": 404}


def price_list(customer_type, storage_id, sub_category, brand, model, allowed_storages):
    result = Product.price_list(customer_type, storage_id, sub_category, brand, model, allowed_storages)
    if result:
        return {"success": True, "message": result, "status_code": 200}
    return {"success": False, "error": "product not found", "status_code": 404}


def get_basket_product(system_code, storage_id, customer_type):
    result = Product.get_basket_product(system_code, storage_id, customer_type)
    if result:
        return {"success": True, "message": result, "status_code": 200}
    return {"success": False, "error": "product not found", "status_code": 404}
