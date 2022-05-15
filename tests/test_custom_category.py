from app.controllers import custom_category
from unittest import mock


@mock.patch('app.models.custom_category.KowsarCategories.create')
def test_create_custom_kowsar_category(mocked_obj):
    mocked_obj.return_value = True
    assert custom_category.create_custom_kowsar_category(
        "10",
        "test",
        True,
        "https://www.google.com",
    ) == {"success": True, "message": "دسته بندی با موفقیت ایجاد شد", "status_code": 201}

    assert custom_category.create_custom_kowsar_category(
        "1001",
        "test",
        True,
        "https://www.google.com",
    ) == {"success": True, "message": "دسته بندی با موفقیت ایجاد شد", "status_code": 201}

    assert custom_category.create_custom_kowsar_category(
        "100101",
        "test",
        True,
        "https://www.google.com",
    ) == {"success": True, "message": "دسته بندی با موفقیت ایجاد شد", "status_code": 201}

    assert custom_category.create_custom_kowsar_category(
        "100101111111",
        "test",
        True,
        "https://www.google.com",
    ) == {"success": False, "error": "سیستم کد وارد شده صحیح نمیباشد", "status_code": 404}

    mocked_obj.return_value = "Category already exists"

    assert custom_category.create_custom_kowsar_category(
        "100101",
        "test",
        True,
        "https://www.google.com",
    ) == {"success": False, "error": "دسته بندی این نام در سیستم موجود است", "status_code": 400}

    mocked_obj.return_value = None

    assert custom_category.create_custom_kowsar_category(
        "100101",
        "test",
        True,
        "https://www.google.com",
    ) == {"success": False, "error": "خطایی در انجام عملیات رخ داد", "status_code": 400}




