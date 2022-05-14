from app.models.custom_category import KowsarCategories


def create_custom_kowsar_category(system_code: str, custom_name: str, visible_in_site: bool):
    """
    Create a custom category for Kowsar
    """
    custom_category = KowsarCategories(system_code, custom_name, visible_in_site)
    result = custom_category.create()
    if result:
        return {"success": True, "message": "دسته بندی با موفقیت ایجاد شد", "status_code": 201}
    return {"success": False, "message": "خطایی در انجام عملیات رخ داد", "status_code": 400}
