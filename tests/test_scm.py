from app.helpers.mongo_connection import MongoConnection
from unittest import mock, TestCase
import jdatetime
import mongomock
from app.controllers.scm_controller import get_product_to_assign_qty, assign_product_inventory
from app.models.scm_quantity import *


class ScmTest(TestCase):

    def setUp(self):
        self.mongo_mock = mock.patch.object(MongoConnection, "client", new=mongomock.MongoClient())

    products = [{
        "system_code": "505050",
        "attributes": {
            "description-pd": "mjygjh",
            "charger-pd": True,
            "handsfree-pd": True,
            "glass-pd": True,
            "case-pd": True,
            "weight-pd": "5465465",
            "screen-pd": "6545456",
            "storage-pd": "122",
            "fa-support-pd": None,
            "mainImage-pd": "https://devapi.aasood.com/gallery_files/product/2000010010001001001001001/mainImage-pd/220x220.jpg",
            "otherImage-pd": "https://devapi.aasood.com/gallery_files/product/2000010010001001001001001/otherImage-pd/220x220.jpg",
            "closeImage-pd": "https://devapi.aasood.com/gallery_files/product/2000010010001001001001001/closeImage-pd/220x220.jpg",
            "simnum-pd": "single"
        },
        "brand": "Samsung",
        "color": "Black",
        "configs": {
            "ram": "1GB",
            "storage": "16GB",
            "network": "4G",
            "region": "Vietnam"
        },
        "guaranty": "Aawaat",
        "main_category": "Device",
        "model": "A01 Core",
        "name": "Mobile Samsung A01 Core (1GB 16GB 4G) Vietnam",
        "seller": "ASD",
        "step": 4,
        "sub_category": "Mobile",
        "warehouse_details": {
            "B2B": {
                "type": "B2B",
                "storages": {
                    "1": {
                        "storage_id": "1",
                        "regular": 31233,
                        "reserved": 40,
                        "quantity": 45,
                        "min_qty": 1,
                        "max_qty": 1,
                        "warehouse_state": "تهران",
                        "warehouse_city": "تهران",
                        "warehouse_state_id": "08",
                        "warehouse_city_id": "1874",
                        "warehouse_label": "مرکزی",
                        "special": None,
                        "informal_price": None,
                        "special_from_date": None,
                        "special_to_date": None,
                        "inventory": 53
                    },
                    "2": {
                        "storage_id": "2",
                        "regular": 1000000000,
                        "reserved": 0,
                        "quantity": 4,
                        "min_qty": 1,
                        "max_qty": 1,
                        "warehouse_state": "خراسان رضوی",
                        "warehouse_city": "مشهد",
                        "warehouse_state_id": "11",
                        "warehouse_city_id": "1871",
                        "warehouse_label": "مشهد"
                    },
                    "3": {
                        "storage_id": "3",
                        "regular": 31231,
                        "informal_price": None,
                        "special": None,
                        "special_from_date": None,
                        "special_to_date": None,
                        "warehouse_state": "زنجان",
                        "warehouse_city": "زنجان",
                        "warehouse_state_id": "14",
                        "warehouse_city_id": "1863",
                        "warehouse_label": "زنجان",
                        "inventory": 0
                    },
                    "7": {
                        "storage_id": "7",
                        "regular": 31231,
                        "informal_price": None,
                        "special": None,
                        "special_from_date": None,
                        "special_to_date": None,
                        "warehouse_state": "تهران",
                        "warehouse_city": "تهران",
                        "warehouse_state_id": "08",
                        "warehouse_city_id": "1874",
                        "warehouse_label": "ولیعصر",
                        "inventory": 0
                    },
                    "8": {
                        "storage_id": "8",
                        "regular": 31231,
                        "informal_price": None,
                        "special": None,
                        "special_from_date": None,
                        "special_to_date": None,
                        "warehouse_state": "فارس",
                        "warehouse_city": "فارس",
                        "warehouse_state_id": "17",
                        "warehouse_city_id": "1859",
                        "warehouse_label": "شیراز",
                        "inventory": 0
                    },
                    "9": {
                        "storage_id": "9",
                        "regular": 31231,
                        "informal_price": None,
                        "special": None,
                        "special_from_date": None,
                        "special_to_date": None,
                        "warehouse_state": "اصفهان",
                        "warehouse_city": "اصفهان",
                        "warehouse_state_id": "04",
                        "warehouse_city_id": "1881",
                        "warehouse_label": "اصفهان",
                        "inventory": 0
                    },
                    "10": {
                        "storage_id": "10",
                        "regular": 31231,
                        "informal_price": None,
                        "special": None,
                        "special_from_date": None,
                        "special_to_date": None,
                        "warehouse_state": "خوزستان",
                        "warehouse_city": "اهواز",
                        "warehouse_state_id": "13",
                        "warehouse_city_id": "1867",
                        "warehouse_label": "اهواز",
                        "inventory": 0
                    }
                }
            },
            "B2C": {
                "type": "B2C",
                "storages": {
                    "1": {
                        "storage_id": "1",
                        "regular": 1230000,
                        "informal_price": None,
                        "special": None,
                        "special_from_date": None,
                        "special_to_date": None,
                        "warehouse_state": "تهران",
                        "warehouse_city": "تهران",
                        "warehouse_state_id": "08",
                        "warehouse_city_id": "1874",
                        "warehouse_label": "مرکزی",
                        "inventory": 1,
                        "quantity": 1,
                        "min_qty": 1,
                        "max_qty": 1
                    },
                    "2": {
                        "storage_id": "2",
                        "regular": 1000000,
                        "informal_price": None,
                        "special": None,
                        "special_from_date": None,
                        "special_to_date": None,
                        "warehouse_state": "خراسان رضوی",
                        "warehouse_city": "مشهد",
                        "warehouse_state_id": 11,
                        "warehouse_city_id": "1871",
                        "warehouse_label": "مشهد",
                        "inventory": 0
                    },
                    "3": {
                        "storage_id": "3",
                        "regular": 1000000,
                        "informal_price": None,
                        "special": None,
                        "special_from_date": None,
                        "special_to_date": None,
                        "warehouse_state": "زنجان",
                        "warehouse_city": "زنجان",
                        "warehouse_state_id": "14",
                        "warehouse_city_id": "1863",
                        "warehouse_label": "زنجان",
                        "inventory": 0
                    },
                    "7": {
                        "storage_id": "7",
                        "regular": 1000000,
                        "informal_price": None,
                        "special": None,
                        "special_from_date": None,
                        "special_to_date": None,
                        "warehouse_state": "تهران",
                        "warehouse_city": "تهران",
                        "warehouse_state_id": "08",
                        "warehouse_city_id": "1874",
                        "warehouse_label": "ولیعصر",
                        "inventory": 0
                    },
                    "8": {
                        "storage_id": "8",
                        "regular": 1000000,
                        "informal_price": None,
                        "special": None,
                        "special_from_date": None,
                        "special_to_date": None,
                        "warehouse_state": "فارس",
                        "warehouse_city": "فارس",
                        "warehouse_state_id": "17",
                        "warehouse_city_id": "1859",
                        "warehouse_label": "شیراز",
                        "inventory": 0
                    },
                    "9": {
                        "storage_id": "9",
                        "regular": 1000000,
                        "informal_price": None,
                        "special": None,
                        "special_from_date": None,
                        "special_to_date": None,
                        "warehouse_state": "اصفهان",
                        "warehouse_city": "اصفهان",
                        "warehouse_state_id": "04",
                        "warehouse_city_id": "1881",
                        "warehouse_label": "اصفهان",
                        "inventory": 0
                    },
                    "10": {
                        "storage_id": "10",
                        "regular": 1000000,
                        "informal_price": None,
                        "special": None,
                        "special_from_date": None,
                        "special_to_date": None,
                        "warehouse_state": "خوزستان",
                        "warehouse_city": "اهواز",
                        "warehouse_state_id": "13",
                        "warehouse_city_id": "1867",
                        "warehouse_label": "اهواز",
                        "inventory": 0
                    }
                }
            },
            "B2G": {
                "type": "B2G"
            }
        },
        "visible_in_site": False,
        "date": "1401-05-13 21:14:52",
        "warehouse_city": "تهران",
        "inventory": {
            "1": {
                "total": 54,
                "unassigned": 54
            },
            "2": {
                "total": 0,
                "unassigned": 0
            },
            "3": {
                "total": 0,
                "unassigned": 0
            },
            "7": {
                "total": 0,
                "unassigned": 0
            },
            "8": {
                "total": 0,
                "unassigned": 0
            },
            "9": {
                "total": 0,
                "unassigned": 0
            },
            "10": {
                "total": 0,
                "unassigned": 0
            }
        }
    }]

    def insert_initial_data(self):
        with self.mongo_mock:
            with MongoConnection() as mongo:
                mongo.product.insert_one(self.products[0])

    def test_get_product_to_assign_qty(self):
        self.insert_initial_data()
        with self.mongo_mock:
            self.assertEqual(
                get_product_to_assign_qty("1", "505051", "B2B"),
                {"message": "محصولی یافت نشد", "success": False, "status_code": 417}
            )
            self.assertEqual(
                get_product_to_assign_qty("114", "505050", "B2B"),
                {"message": "محصولی با نوع مشتری ویا کد انبار مورد نظر یافت نشد", "success": False, "status_code": 417}
            )
            message = {
                "storage_id": "1",
                "regular": 31233,
                "reserved": 40,
                "quantity": 45,
                "min_qty": 1,
                "max_qty": 1,
                "warehouse_state": "تهران",
                "warehouse_city": "تهران",
                "warehouse_state_id": "08",
                "warehouse_city_id": "1874",
                "warehouse_label": "مرکزی",
                "special": None,
                "informal_price": None,
                "special_from_date": None,
                "special_to_date": None,
                "inventory": 53
            }
            self.assertEqual(
                get_product_to_assign_qty("1", "505050", "B2B"),
                {"message": message, "success": True, "status_code": 200}
            )

    def test_assign_product_inventory(self):
        self.insert_initial_data()
        with self.mongo_mock:
            self.assertEqual(
                assign_product_inventory("1", "505050", "B2B", False, None, 10, 1, 1, None, 1, "admin"),
                {"message": "تغییر موجودی مجاز نمی باشد", "success": False, "status_code": 417}
            )
            self.assertEqual(
                assign_product_inventory("1", "505050", "B2B", False, None, 60, 1, 1, None, 1, "admin"),
                {"message": "تعداد تخصیص داده شده بیشتر از موجودی می باشد", "success": False, "status_code": 417}
            )
            self.assertEqual(
                assign_product_inventory("1", "505050", "B2B", True, "B2C", 9, 1, 1, 10000, 1, "admin"),
                {"message": "مجاز به انتقال نمی باشید", "success": False, "status_code": 417}
            )
            self.assertEqual(
                assign_product_inventory("1", "505050", "B2B", True, "B2C", 5, 1, 1, 10000, 1, "admin"),
                {"message": "عملیات با موفقیت انجام شد", "success": True, "status_code": 200}
            )
            self.assertEqual(
                assign_product_inventory("1", "505050", "B2B", False, None, 49, 1, 1, None, 1, "admin"),
                {"message": "تعداد تخصیص داده شده بیشتر از موجودی می باشد", "success": False, "status_code": 417}
            )
            self.assertEqual(
                assign_product_inventory("1", "505050", "B2B", False, None, 47, 1, 1, None, 1, "admin"),
                {"message": "عملیات با موفقیت انجام شد", "success": True, "status_code": 200}
            )
