from unittest import mock

import mongomock

from app.controllers import custom_category
from app.helpers.mongo_connection import MongoConnection


def test_create_custom_kowsar_category_fixture():
    with MongoConnection() as client:
        client.kowsar_collection.insert_many(
            [
                {
                    "system_code": "10",
                    "main_category": "Device",
                },
                {
                    "system_code": "1001",
                    "main_category": "Device",
                    "sub_category": "Mobile",
                },
                {
                    "system_code": "100101",
                    "brand": "Mobile Sumsung",
                    "main_category": "Device",
                    "sub_category": "Mobile",
                }
            ]
        )


@mock.patch.object(MongoConnection, "client", new_callable=mongomock.MongoClient)
def test_create_custom_kowsar_category(mocked_obj):
    test_create_custom_kowsar_category_fixture()
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

    assert custom_category.create_custom_kowsar_category(
        "100101",
        "test",
        True,
        "https://www.google.com",
    ) == {"success": False, "error": "دسته بندی این نام در سیستم موجود است", "status_code": 400}

    with mock.patch("app.models.custom_category.KowsarCategories.create", return_value=None):
        assert custom_category.create_custom_kowsar_category(
            "100101",
            "test",
            True,
            "https://www.google.com",
        ) == {"success": False, "error": "خطایی در انجام عملیات رخ داد", "status_code": 400}


@mock.patch.object(MongoConnection, "client", new_callable=mongomock.MongoClient)
def test_create_custom_category(mocked_obj):
    assert custom_category.create_custom_category(
        "test",
        ["10", "11"],
        "تست",
        True,
        "https://www.google.com",
    ) == {"success": True, "message": "دسته بندی با موفقیت ایجاد شد", "status_code": 201}

    assert custom_category.create_custom_category(
        "test",
        ["10", "11"],
        "تست",
        True,
        "https://www.google.com",
    ) == {"success": False, "error": "دسته بندی این نام در سیستم موجود است", "status_code": 400}

    with mock.patch("app.models.custom_category.CustomCategories.create", return_value=None):
        with mock.patch("app.models.custom_category.CustomCategories.is_unique", return_value=True):
            assert custom_category.create_custom_category(
                "test",
                ["10", "11"],
                "تست",
                True,
                "https://www.google.com",
            ) == {"success": False, "error": "خطایی در انجام عملیات رخ داد", "status_code": 400}
