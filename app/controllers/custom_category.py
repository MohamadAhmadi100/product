from app.models.custom_category import KowsarCategories, CustomCategories
from app.models.product import Product


def create_custom_kowsar_category(system_code: str, custom_name: str, visible_in_site: bool, image: str):
    """
    Create a custom name and image and change visibility of Kowsar categories
    """
    custom_category = KowsarCategories(system_code, custom_name, visible_in_site, image)
    if len(system_code) == 2:
        category_label = "main_category_label"
    elif len(system_code) == 6:
        category_label = "sub_category_label"
    elif len(system_code) == 9:
        category_label = "brand_label"
    else:
        return {"success": False, "error": "سیستم کد وارد شده صحیح نمیباشد", "status_code": 404}

    result = custom_category.create(category_label)
    if result:
        if result == "Category already exists":
            return {"success": False, "error": "دسته بندی این نام در سیستم موجود است", "status_code": 400}
        return {"success": True, "message": "دسته بندی با موفقیت ایجاد شد", "status_code": 201}
    return {"success": False, "error": "خطایی در انجام عملیات رخ داد", "status_code": 400}


def create_custom_category(name: str, products: list, label: str, visible_in_site: bool, image: str):
    """
    Create a custom custom category for products
    """
    custom_category = CustomCategories(name, products, label, visible_in_site, image)
    if custom_category.is_unique():
        result = custom_category.create()
        if result:
            return {"success": True, "message": "دسته بندی با موفقیت ایجاد شد", "status_code": 201}
        return {"success": False, "error": "خطایی در انجام عملیات رخ داد", "status_code": 400}
    return {"success": False, "error": "دسته بندی این نام در سیستم موجود است", "status_code": 400}


def get_categories_products(system_code: str, page: int, per_page: int):
    """
    Get products of a category by systemcode
    """
    result = KowsarCategories.get(system_code, page, per_page)
    return {"success": True, "message": result, "status_code": 200}


def get_custom_category_list(visible_in_site, page: int, per_page: int, created_at_from: str, created_at_to: str):
    """
    Get created custom categories
    """
    result = CustomCategories.get(visible_in_site, page, per_page, created_at_from, created_at_to)
    if result:
        for category in result['data']:
            product_list = []
            for system_code in category['products']:
                product_detail = Product.get_product_child(system_code, "fa_ir")
                product_list.append(product_detail.get("product"))
            category['products'] = product_list
    return {"success": True, "message": result, "status_code": 200}


def get_all_categories():
    """
    """
    result = KowsarCategories.get_all_categories()
    if result:
        return {"success": True, "message": result, "status_code": 200}
    return {"success": False, "error": "categories not found", "status_code": 404}


def delete_custom_category(name: str):
    """
    Delete a custom category
    """
    result = CustomCategories.delete(name)
    if result:
        return {"success": True, "message": "custom category deleted successfully", "status_code": 200}
    return {"success": False, "error": "custom category not found", "status_code": 404}


def edit_custom_category(name: str, new_name: str, products: list, label: str, visible_in_site: bool, image: str):
    """
    editing custom category
    """
    result, message = CustomCategories.edit(name, new_name, products, label, visible_in_site, image)
    if result:
        return {"success": True, "message": message, "status_code": 200}
    return {"success": False, "error": message, "status_code": 400}
