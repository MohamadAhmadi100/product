from unittest import mock, TestCase

import mongomock

from app.controllers import custom_category
from app.helpers.mongo_connection import MongoConnection


class TestCustomCategory(TestCase):

    def setUp(self):
        self.mongo_mock = mock.patch.object(MongoConnection, "client", new=mongomock.MongoClient())

        with self.mongo_mock, MongoConnection() as client:
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

            client.custom_category.insert_many(
                [
                    {
                        "name": "1",
                        "products": ["1", "1"],
                        "label": "1",
                        "visible_in_site": True,
                        "image": "https://google.com",
                        "created_at": "1401-02-26 12:30:07"
                    },
                    {
                        "name": "2",
                        "products": ["2", "2"],
                        "label": "2",
                        "visible_in_site": False,
                        "image": "https://google.com",
                        "created_at": "1401-02-28 12:30:07"
                    }
                ]
            )

    def test_create_custom_kowsar_category(self):
        with self.mongo_mock:
            self.assertEqual(custom_category.create_custom_kowsar_category(
                "10",
                "test",
                True,
                "https://www.google.com",
            ), {"success": True, "message": "دسته بندی با موفقیت ایجاد شد", "status_code": 201})

            self.assertEqual(custom_category.create_custom_kowsar_category(
                "1001",
                "test",
                True,
                "https://www.google.com",
            ), {"success": True, "message": "دسته بندی با موفقیت ایجاد شد", "status_code": 201})

            self.assertEqual(custom_category.create_custom_kowsar_category(
                "100101",
                "test",
                True,
                "https://www.google.com",
            ), {"success": True, "message": "دسته بندی با موفقیت ایجاد شد", "status_code": 201})

            self.assertEqual(custom_category.create_custom_kowsar_category(
                "100101111111",
                "test",
                True,
                "https://www.google.com",
            ), {"success": False, "error": "سیستم کد وارد شده صحیح نمیباشد", "status_code": 404})

            self.assertEqual(custom_category.create_custom_kowsar_category(
                "100101",
                "test",
                True,
                "https://www.google.com",
            ), {"success": False, "error": "دسته بندی این نام در سیستم موجود است", "status_code": 400})

            with mock.patch("app.models.custom_category.KowsarCategories.create", return_value=None):
                self.assertEqual(custom_category.create_custom_kowsar_category(
                    "100101",
                    "test",
                    True,
                    "https://www.google.com",
                ), {"success": False, "error": "خطایی در انجام عملیات رخ داد", "status_code": 400})

    def test_create_custom_category(self):
        with self.mongo_mock:
            self.assertEqual(custom_category.create_custom_category(
                "test",
                ["10", "11"],
                "تست",
                True,
                "https://www.google.com",
            ), {"success": True, "message": "دسته بندی با موفقیت ایجاد شد", "status_code": 201})

            self.assertEqual(custom_category.create_custom_category(
                "test",
                ["10", "11"],
                "تست",
                True,
                "https://www.google.com",
            ), {"success": False, "error": "دسته بندی این نام در سیستم موجود است", "status_code": 400})

            with mock.patch("app.models.custom_category.CustomCategories.create", return_value=None):
                with mock.patch("app.models.custom_category.CustomCategories.is_unique", return_value=True):
                    self.assertEqual(custom_category.create_custom_category(
                        "test",
                        ["10", "11"],
                        "تست",
                        True,
                        "https://www.google.com",
                    ), {"success": False, "error": "خطایی در انجام عملیات رخ داد", "status_code": 400})

    def test_get_custom_category_list(self):
        with self.mongo_mock:
            self.assertEqual(custom_category.get_custom_category_list(None, 1, 10, None, None),
                             {"success": True, "message": {
                                 "total": 2,
                                 "data": [
                                     {
                                         "name": "1",
                                         "products": ["1", "1"],
                                         "label": "1",
                                         "visible_in_site": True,
                                         "image": "https://google.com",
                                         "created_at": "1401-02-26 12:30:07"
                                     },
                                     {
                                         "name": "2",
                                         "products": ["2", "2"],
                                         "label": "2",
                                         "visible_in_site": False,
                                         "image": "https://google.com",
                                         "created_at": "1401-02-28 12:30:07"
                                     }
                                 ]
                             }, "status_code": 200}
                             )

            self.assertEqual(custom_category.get_custom_category_list(True, 1, 10, None, None),
                             {"success": True, "message": {
                                 "total": 1,
                                 "data": [
                                     {
                                         "name": "1",
                                         "products": ["1", "1"],
                                         "label": "1",
                                         "visible_in_site": True,
                                         "image": "https://google.com",
                                         "created_at": "1401-02-26 12:30:07"
                                     }
                                 ]
                             }, "status_code": 200}
                             )

            self.assertEqual(custom_category.get_custom_category_list(None, 1, 10, "1401-02-27 12:30:07", None),
                             {"success": True, "message": {
                                 "total": 1,
                                 "data": [
                                     {
                                         "name": "2",
                                         "products": ["2", "2"],
                                         "label": "2",
                                         "visible_in_site": False,
                                         "image": "https://google.com",
                                         "created_at": "1401-02-28 12:30:07"
                                     }
                                 ]
                             }, "status_code": 200}
                             )

            self.assertEqual(custom_category.get_custom_category_list(None, 1, 10, None, "1401-02-27 12:30:07"),
                             {"success": True, "message": {
                                 "total": 1,
                                 "data": [
                                     {
                                         "name": "1",
                                         "products": ["1", "1"],
                                         "label": "1",
                                         "visible_in_site": True,
                                         "image": "https://google.com",
                                         "created_at": "1401-02-26 12:30:07"
                                     }
                                 ]
                             }, "status_code": 200}
                             )
