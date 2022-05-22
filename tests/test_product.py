import unittest
from unittest import mock

import fakeredis
import mongomock

from app.controllers.kowsar_controller import update_kowsar_collection
from app.helpers.redis_connection import RedisConnection
from tests.conftest import *
from app.controllers.product_controller import *


# def test_get_parent_configs():
#     response = get_parent_configs("100101001")
#     [obj.pop("created") for obj in response['message']]
#     assert response == {"success": True, "message": [
#         {
#             "system_code": "10010100101",
#             "main_category": "Device",
#             "sub_category": "Mobile",
#             "brand": "Mobile Sumsung",
#             "model": "A260",
#             "attributes": {
#                 "storage": "16 GB",
#                 "ram": None
#             },
#         },
#         {
#             "system_code": "10010100102",
#             "main_category": "Device",
#             "sub_category": "Mobile",
#             "brand": "Mobile Sumsung",
#             "model": "A260",
#             "attributes": {
#                 "storage": "8 GB",
#                 "ram": "1 GB"
#             },
#         }
#     ], "status_code": 200}
#     second_response = get_parent_configs("99999999999999")
#     assert second_response == {"success": False, "error": "parent configs not found", "status_code": 404}
#
#
# def test_create_parent(create_parent_fixture):
#     resource = create_parent('10011000101', name="محصول تست", visible_in_site=True)
#     assert resource == {"success": True,
#                         "message": {"message": "product created successfully", "label": "محصول با موفقیت ساخته شد"},
#                         "status_code": 200}
#     second_response = create_parent('99999999999999', name="محصول تست", visible_in_site=True)
#     assert second_response == {"success": False,
#                                "error": {"error": "product not found in kowsar", "label": "محصول در کوثر یافت نشد"},
#                                "status_code": 400}
#     third_response = create_parent('10011000101', name="محصول تست", visible_in_site=True)
#     assert third_response == {"success": False, "error": "system code is not unique", "status_code": 400}
#
#
# def test_suggest_product():
#     response = suggest_product("10011000101")
#     assert response == {"success": True, "message": [
#         {
#             "system_code": "100110001001",
#             "configs": {
#                 "storage": {
#                     "value": "128 GB",
#                     "attribute_label": "حافظه داخلی",
#                     "label": "۱۲۸ گیگابایت"
#                 },
#                 "color": {
#                     "value": "blue",
#                     "attribute_label": "رنگ",
#                     "label": "آبی"
#                 },
#                 "guarantee": {
#                     "value": "sherkati",
#                     "attribute_label": "گارانتی",
#                     "label": "شرکتی"
#                 },
#                 "ram": {
#                     "value": "4 GB",
#                     "attribute_label": "رم",
#                     "label": "۴ گیگابایت"
#                 },
#                 "seller": {
#                     "value": "TejaratKhane Haj Ghasem",
#                     "attribute_label": "فروشنده",
#                     "label": "تجارت خانه حاجی قاسم"
#                 }
#             }
#         }
#     ], "status_code": 200}
#     second_response = suggest_product("99999999999999")
#     assert second_response == {'error': 'parent configs not found', 'status_code': 404, 'success': False}
#
#
# def test_create_child(create_child_fixture):
#     third_response = create_child("100110001001", "hi", True)
#     assert third_response == {'error': {'error': 'product creation 100110001001 failed',
#                                         'label': 'فرایند ساخت محصول 100110001001 به مشکل خورد'},
#                               'status_code': 400,
#                               'success': False}
#     response = create_child("100110001001", "10011000101", True)
#     assert response == {"success": True, "message": {"message": "product 100110001001 created successfully",
#                                                      "label": "محصول 100110001001 با موفقیت ساخته شد"},
#                         "status_code": 201}
#     second_response = create_child("100110001001", "10011000101", True)
#     assert second_response == {"success": False, "error": "child system code is not unique", "status_code": 400}
#     fourth_response = create_child("99999999999999", "99999999999999", True)
#     assert fourth_response == {'error': {'error': 'product not found in kowsar',
#                                          'label': 'محصول در کوثر یافت نشد'},
#                                'status_code': 400,
#                                'success': False}
#
#
# def test_add_attributes(add_attributes_fixture):
#     response = add_attributes("100110001001", {
#         "image": "/src/default.jpg",
#         "year": 2020
#     })
#     assert response == {"success": True,
#                         "message": {"message": "attribute added successfully", "label": "صفت با موفقیت اضافه شد"},
#                         "status_code": 201}
#
#     second_response = add_attributes("10011000101", {
#         "image": "/src/default.jpg",
#         "year": 2020
#     })
#     assert second_response == {"success": False, "error": "system code not found", "status_code": 400}
#     third_response = add_attributes("100110001001", {
#         "image": "/src/default.jpg",
#         "year": 2020
#     })
#     assert third_response == {"success": False,
#                               "error": {"error": "attribute add failed", "label": "فرایند افزودن صفت به مشکل برخورد"},
#                               "status_code": 400}
#     fourth_response = add_attributes("99999999999999", {"image": "/src/default.jpg", "year": 2020})
#     assert fourth_response == {"success": False, "error": "system code not found", "status_code": 400}
#
#
# def test_get_product_by_system_code(get_product_by_system_code_fixture):
#     response = get_product_by_system_code("10011000101", "fa_ir")
#     response['message'].pop("date")
#     response['message'].pop("jalali_date")
#     for pro in response['message']['products']:
#         pro.pop("date")
#         pro.pop("jalali_date")
#     assert response == {'message': {'attributes': {'ram': '4 GB', 'storage': '128 GB'},
#                                     'brand': 'Mobile LG',
#                                     'main_category': 'Device',
#                                     'model': 'K61',
#                                     'name': 'محصول تست',
#                                     'products': [{'attributes': {'image': '/src/default.jpg',
#                                                                  'year': 2020},
#                                                   'config': {'color': {'attribute_label': 'رنگ',
#                                                                        'label': 'آبی',
#                                                                        'value': 'blue'},
#                                                              'guarantee': {'attribute_label': 'گارانتی',
#                                                                            'label': 'شرکتی',
#                                                                            'value': 'sherkati'},
#                                                              'ram': {'attribute_label': 'رم',
#                                                                      'label': '۴ گیگابایت',
#                                                                      'value': '4 GB'},
#                                                              'seller': {'attribute_label': 'فروشنده',
#                                                                         'label': 'تجارت خانه حاجی '
#                                                                                  'قاسم',
#                                                                         'value': 'TejaratKhane Haj '
#                                                                                  'Ghasem'},
#                                                              'storage': {'attribute_label': 'حافظه '
#                                                                                             'داخلی',
#                                                                          'label': '۱۲۸ گیگابایت',
#                                                                          'value': '128 GB'}},
#                                                   'system_code': '100110001001',
#                                                   'visible_in_site': True}],
#                                     'routes': {'child': {'child': {'label': 'موبایل ال جی',
#                                                                    'route': 'Mobile LG'},
#                                                          'label': 'موبایل',
#                                                          'route': 'Mobile'},
#                                                'label': 'دستگاه',
#                                                'route': 'Device'},
#                                     'sub_category': 'Mobile',
#                                     'system_code': '10011000101',
#                                     'visible_in_site': True},
#                         'status_code': 200,
#                         'success': True}
#     second_response = get_product_by_system_code("99999999999", "fa_ir")
#     assert second_response == {"success": False, "error": "product not found", "status_code": 404}
#
#
# def test_delete_product(delete_product_fixure):
#     response = delete_product("100110001001")
#     assert response == {"success": True,
#                         "message": {"message": "product archived successfully", "label": "محصول با موفقیت حذف شد"},
#                         "status_code": 200}
#
#     second_response = delete_product("99999999999")
#     assert second_response == {"success": False, "error": "product not found", "status_code": 404}
#     third_response = delete_product("100110001001")
#     assert third_response == {"success": False,
#                               "error": {"message": "product failed to archive", "label": "حذف محصول با خطا مواجه شد"},
#                               "status_code": 400}
#
#
# def test_update_attribute_collection():
#     response = update_attribute_collection([
#         {
#             "required": True,
#             "use_in_filter": False,
#             "use_for_sort": False,
#             "default_value": None,
#             "values": None,
#             "set_to_nodes": False,
#             "name": "year",
#             "label": "سال",
#             "input_type": "Number",
#             "parent": "100104021006"
#         },
#         {
#             "required": False,
#             "use_in_filter": False,
#             "use_for_sort": False,
#             "default_value": "/src/default.png",
#             "values": None,
#             "set_to_nodes": True,
#             "name": "image",
#             "label": "عکس",
#             "input_type": "Media Image",
#             "parent": "1001"
#         }
#     ])
#     assert response == {"success": True, "message": {"message": "attribute collection updated"}, "status_code": 200}
#
#
# def test_get_all_categories():
#     response = get_all_categories("00", 1, 2)
#     assert response == {'message': [{'label': 'Accessory', 'system_code': '12'},
#                                     {'label': 'Device', 'system_code': '10'}],
#                         'status_code': 200,
#                         'success': True} or {
#                'message': [{'label': 'Device', 'system_code': '10'}, {'label': 'Accessory', 'system_code': '12'}],
#                'status_code': 200,
#                'success': True}
#     second_response = get_all_categories("99", 1, 2)
#     assert second_response == {"success": False, "error": "categories not found", "status_code": 404}
#

class ProductTest(unittest.TestCase):
    def setUp(self):
        self.mongo_mock = mock.patch.object(MongoConnection, "client", new=mongomock.MongoClient())
        self.redis_mock = mock.patch.object(RedisConnection, "client",
                                            new=fakeredis.FakeStrictRedis(decode_responses=True))
        with self.mongo_mock, self.redis_mock:
            self.update_kowsar_collection = update_kowsar_collection()

    def test_get_parent_configs(self):
        with self.mongo_mock, self.redis_mock:
            response = get_parent_configs("100101001")
            self.assertEqual({"success": True, "message": [
                {
                    "system_code": "10010100101",
                    "main_category": "Device",
                    "sub_category": "Mobile",
                    "brand": "Mobile Sumsung",
                    "model": "A260",
                    "attributes": {
                        "storage": "16 GB",
                        "ram": None
                    },
                },
                {
                    "system_code": "10010100102",
                    "main_category": "Device",
                    "sub_category": "Mobile",
                    "brand": "Mobile Sumsung",
                    "model": "A260",
                    "attributes": {
                        "storage": "8 GB",
                        "ram": "1 GB"
                    },
                }
            ], "status_code": 200}, response)

            second_response = get_parent_configs("99999999999999")
            self.assertEqual({"success": False, "error": "parent configs not found", "status_code": 404},
                             second_response)

    def create_parents_func(self):
        with self.mongo_mock, self.redis_mock:
            self.create_parents_first_response = create_parent('10011000101', name="محصول تست", url_name="test")
            self.create_parents_second_response = create_parent('10011000101', name="محصول تست", url_name="test")
            self.create_parents_third_response = create_parent('99999999999999', name="محصول تست", url_name="test")

    def test_suggest_product(self):
        with self.mongo_mock, self.redis_mock:
            response = suggest_product("10011000101")
            self.assertEqual({'message': [{'configs': {'color': {'attribute_label': 'رنگ',
                                                                 'label': 'آبی',
                                                                 'value': 'blue'},
                                                       'guarantee': {'attribute_label': 'گارانتی',
                                                                     'label': 'شرکتی',
                                                                     'value': 'sherkati'},
                                                       'ram': {'attribute_label': 'رم',
                                                               'label': '۴ گیگابایت',
                                                               'value': '4 GB'},
                                                       'seller': {'attribute_label': 'فروشنده',
                                                                  'label': 'تجارت خانه حاجی قاسم',
                                                                  'value': 'TejaratKhane Haj Ghasem'},
                                                       'storage': {'attribute_label': 'حافظه داخلی',
                                                                   'label': '۱۲۸ گیگابایت',
                                                                   'value': '128 GB'}},
                                           'system_code': '100110001001'}],
                              'status_code': 200,
                              'success': True}, response)

            second_response = suggest_product("99999999999999")
            self.assertEqual({"success": False, "error": "parent configs not found", "status_code": 404},
                             second_response)
