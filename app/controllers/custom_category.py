from app.models.custom_category import KowsarCategories


def create_custom_kowsar_category(system_code: str, custom_name: str, visible_in_site: bool, image: str):
    """
    Create a custom name and image and change visibility of Kowsar categories
    """
    custom_category = KowsarCategories(system_code, custom_name, visible_in_site, image)
    if len(system_code) == 2:
        category_label = "main_category_label"
    elif len(system_code) == 4:
        category_label = "sub_category_label"
    elif len(system_code) == 6:
        category_label = "brand_label"
    else:
        return {"success": False, "error": "سیستم کد وارد شده صحیح نمیباشد", "status_code": 404}

    result = custom_category.create(category_label)
    if result:
        if result == "Category already exists":
            return {"success": False, "error": "دسته بندی این نام در سیستم موجود است", "status_code": 400}
        return {"success": True, "message": "دسته بندی با موفقیت ایجاد شد", "status_code": 201}
    return {"success": False, "error": "خطایی در انجام عملیات رخ داد", "status_code": 400}
