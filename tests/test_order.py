from app.helpers.mongo_connection import MongoConnection
from unittest import mock, TestCase
import jdatetime
import mongomock
from app.models.order import *
from app.controllers.order import exit_order_handler, exit_order


class OrderTest(TestCase):

    def setUp(self):
        self.mongo_mock = mock.patch.object(MongoConnection, "client", new=mongomock.MongoClient())

    imes = [
        {
            "type": "imeis",
            "system_code": "12345",
            "name": "Samsung A52s (8GB 256GB 5G) Vietnam | ASD | Aawaat [Black]",
            "brand": "Samsung",
            "model": "A52s",
            "color": "Black",
            "guaranty": "Aawaat",
            "seller": "ASD",
            "stock_label": "زنجان",
            "storage_id": "1",
            "imeis": [{
                "imei": "1"
            }, {
                "imei": "2"
            }, {
                "imei": "3"
            }, {
                "imei": "5"
            }, {
                "imei": "4"
            }]
        },
        {
            "type": "imeis",
            "system_code": "678910",
            "name": "Samsung A52s (8GB 256GB 5G) Vietnam | ASD | Aawaat [Black]",
            "brand": "Samsung",
            "model": "A52s",
            "color": "Black",
            "guaranty": "Aawaat",
            "seller": "ASD",
            "stock_label": "زنجان",
            "storage_id": "1",
            "imeis": [{
                "imei": "6"
            }, {
                "imei": "7"
            }, {
                "imei": "10"
            }, {
                "imei": "9"
            }, {
                "imei": "8"
            }]
        }
    ]
    archive = [
        {
            "referral_number": 9,
            "system_code": "678910",
            "name": "Samsung A12 Nacho (4GB 64GB 4G) India | ASD | Sherkati [Black]",
            "supplier_name": "اسود",
            "form_date": "1401-05-14 23:25:00",
            "insert_date": "1401-05-15 12:20:55",
            "unit_price": 4325310,
            "sell_price": 4369000,
            "articles": [{
                "first": "6",
                "exist": True,
                "type": "physical",
                "stockId": "1",
                "stockName": "مشهد",
                "stockLabel": "مشهد",
                "stockState": "خراسان رضوی",
                "stockCity": "مشهد",
                "stockStateId": 11,
                "stockCityId": "1871",
                "name": "Samsung A12 Nacho (4GB 64GB 4G) India | ASD | Sherkati [Black]",
                "status": "landed"
            }, {
                "first": "7",
                "exist": True,
                "type": "physical",
                "stockId": "1",
                "stockName": "مشهد",
                "stockLabel": "مشهد",
                "stockState": "خراسان رضوی",
                "stockCity": "مشهد",
                "stockStateId": 11,
                "stockCityId": "1871",
                "name": "Samsung A12 Nacho (4GB 64GB 4G) India | ASD | Sherkati [Black]",
                "status": "landed"
            }, {
                "first": "8",
                "exist": True,
                "type": "physical",
                "stockId": "1",
                "stockName": "مشهد",
                "stockLabel": "مشهد",
                "stockState": "خراسان رضوی",
                "stockCity": "مشهد",
                "stockStateId": 11,
                "stockCityId": "1871",
                "name": "Samsung A12 Nacho (4GB 64GB 4G) India | ASD | Sherkati [Black]",
                "status": "landed"
            }, {
                "first": "9",
                "exist": True,
                "type": "physical",
                "stockId": "1",
                "stockName": "مشهد",
                "stockLabel": "مشهد",
                "stockState": "خراسان رضوی",
                "stockCity": "مشهد",
                "stockStateId": 11,
                "stockCityId": "1871",
                "name": "Samsung A12 Nacho (4GB 64GB 4G) India | ASD | Sherkati [Black]",
                "status": "landed"
            }, {
                "first": "10",
                "exist": True,
                "type": "physical",
                "stockId": "1",
                "stockName": "مشهد",
                "stockLabel": "مشهد",
                "stockState": "خراسان رضوی",
                "stockCity": "مشهد",
                "stockStateId": 11,
                "stockCityId": "1871",
                "name": "Samsung A12 Nacho (4GB 64GB 4G) India | ASD | Sherkati [Black]",
                "status": "landed"
            }]
        },
        {
            "referral_number": 9,
            "system_code": "12345",
            "name": "Samsung A12 Nacho (4GB 64GB 4G) India | ASD | Sherkati [Black]",
            "supplier_name": "اسود",
            "form_date": "1401-05-14 23:25:00",
            "insert_date": "1401-05-15 12:20:55",
            "unit_price": 4325310,
            "sell_price": 4369000,
            "articles": [{
                "first": "1",
                "exist": True,
                "type": "physical",
                "stockId": "1",
                "stockName": "مشهد",
                "stockLabel": "مشهد",
                "stockState": "خراسان رضوی",
                "stockCity": "مشهد",
                "stockStateId": 11,
                "stockCityId": "1871",
                "name": "Samsung A12 Nacho (4GB 64GB 4G) India | ASD | Sherkati [Black]",
                "status": "landed"
            }, {
                "first": "2",
                "exist": True,
                "type": "physical",
                "stockId": "1",
                "stockName": "مشهد",
                "stockLabel": "مشهد",
                "stockState": "خراسان رضوی",
                "stockCity": "مشهد",
                "stockStateId": 11,
                "stockCityId": "1871",
                "name": "Samsung A12 Nacho (4GB 64GB 4G) India | ASD | Sherkati [Black]",
                "status": "landed"
            }, {
                "first": "3",
                "exist": True,
                "type": "physical",
                "stockId": "1",
                "stockName": "مشهد",
                "stockLabel": "مشهد",
                "stockState": "خراسان رضوی",
                "stockCity": "مشهد",
                "stockStateId": 11,
                "stockCityId": "1871",
                "name": "Samsung A12 Nacho (4GB 64GB 4G) India | ASD | Sherkati [Black]",
                "status": "landed"
            }, {
                "first": "4",
                "exist": True,
                "type": "physical",
                "stockId": "1",
                "stockName": "مشهد",
                "stockLabel": "مشهد",
                "stockState": "خراسان رضوی",
                "stockCity": "مشهد",
                "stockStateId": 11,
                "stockCityId": "1871",
                "name": "Samsung A12 Nacho (4GB 64GB 4G) India | ASD | Sherkati [Black]",
                "status": "landed"
            }, {
                "first": "5",
                "exist": True,
                "type": "physical",
                "stockId": "1",
                "stockName": "مشهد",
                "stockLabel": "مشهد",
                "stockState": "خراسان رضوی",
                "stockCity": "مشهد",
                "stockStateId": 11,
                "stockCityId": "1871",
                "name": "Samsung A12 Nacho (4GB 64GB 4G) India | ASD | Sherkati [Black]",
                "status": "landed"
            }]
        }
    ]

    products = [
        {
            "system_code": "12345",
            "attributes": {
                "description-pd": None,
                "charger-pd": None,
                "handsfree-pd": None,
                "glass-pd": None,
                "case-pd": None,
                "weight-pd": None,
                "screen-pd": None,
                "storage-pd": None,
                "fa-support-pd": None,
                "mainImage-pd": "https://devapi.aasood.com/gallery_files/product/2000010010001001001005001/mainImage-pd/220x220.jpg",
                "otherImage-pd": "https://devapi.aasood.com/gallery_files/product/2000010010001001001005001/otherImage-pd/220x220.jpg",
                "closeImage-pd": "https://devapi.aasood.com/gallery_files/product/2000010010001001001005001/closeImage-pd/220x220.jpg",
                "simnum-pd": "dual"
            },
            "brand": "Samsung",
            "color": "Blue",
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
                            "regular": 31231,
                            "reserved": 5,
                            "quantity": 10,
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
                            "special_to_date": None
                        },
                        "2": {
                            "storage_id": "2",
                            "regular": 31231,
                            "informal_price": None,
                            "special": None,
                            "special_from_date": None,
                            "special_to_date": None,
                            "warehouse_state": "خراسان رضوی",
                            "warehouse_city": "مشهد",
                            "warehouse_state_id": 11,
                            "warehouse_city_id": "1871",
                            "warehouse_label": "مشهد"
                        },
                    },
                },
                "B2G": {
                    "type": "B2G"
                }
            },
            "visible_in_site": False,
            "date": "1401-05-13 21:14:52"
        },
        {
            "system_code": "678910",
            "attributes": {
                "description-pd": None,
                "charger-pd": None,
                "handsfree-pd": None,
                "glass-pd": None,
                "case-pd": None,
                "weight-pd": None,
                "screen-pd": None,
                "storage-pd": None,
                "fa-support-pd": None,
                "mainImage-pd": "https://devapi.aasood.com/gallery_files/product/2000010010001001001005001/mainImage-pd/220x220.jpg",
                "otherImage-pd": "https://devapi.aasood.com/gallery_files/product/2000010010001001001005001/otherImage-pd/220x220.jpg",
                "closeImage-pd": "https://devapi.aasood.com/gallery_files/product/2000010010001001001005001/closeImage-pd/220x220.jpg",
                "simnum-pd": "dual"
            },
            "brand": "Samsung",
            "color": "Blue",
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
                            "regular": 31231,
                            "reserved": 5,
                            "quantity": 10,
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
                            "special_to_date": None
                        }},
                    "B2G": {
                        "type": "B2G"
                    }
                },
                "visible_in_site": False,
                "date": "1401-05-13 21:14:52"
            }}
    ]

    def insert_initial_data(self):
        with self.mongo_mock:
            with MongoConnection() as mongo:
                for imei in self.imes:
                    mongo.imeis.insert_one(imei)
                for arch in self.archive:
                    mongo.archive.insert_one(arch)
                for pro in self.products:
                    mongo.product.insert_one(pro)



    def test_exit_order(self):
        self.insert_initial_data()
        with self.mongo_mock:
            exit_product = [
                {
                    "system_code": "12345",
                    "imeis": ["1", "2", "3", "4", "5"]

                },
                {
                    "system_code": "678910",
                    "imeis": ["6", "7", "18", "9", "10"]

                }
            ]
            exit_product2 = [
                {
                    "system_code": "12345",
                    "imeis": ["1", "2", "3", "4", "5"]

                },
                {
                    "system_code": "6789105",
                    "imeis": ["6", "7", "8", "9", "10"]

                }
            ]

            exit_product3 = [
                {
                    "system_code": "12345",
                    "imeis": ["1", "2", "3", "4", "5"]

                },
                {
                    "system_code": "678910",
                    "imeis": ["6", "7", "8", "9", "10"]

                }
            ]

            rollback_obj = [{

                "orderNumber": 111,
                "storageId": "1",
                "systemCode": "12345",
                "count": 5,
                "staffId": "1221",
                "staffName": "dalam",
                "imeis": ["1", "2", "3", "4", "5"],
                'customerType': 'B2B',
            },
                {"orderNumber": 111,
                 "storageId": "1",
                 "systemCode": "678910",
                 "count": 5,
                 "staffId": "1221",
                 "staffName": "dalam",
                 "imeis": ["6", "7", "8", "9", "10"],
                 'customerType': 'B2B',
                 }
            ]

            self.assertEqual(
                exit_order(111, "1", exit_product, "1221", "dalam","B2B"),
                {"message": "خطا در چک imei", "success": False, "status_code": 417}
            )
            self.assertEqual(
                exit_order(111, "1", exit_product2, "1221", "dalam","B2B"),
                {"message": "مغایرت در سیستم کد", "success": False, "status_code": 417}
            )
            self.assertEqual(
                exit_order(111, "1", exit_product3, "1221", "dalam","B2B"),
                {"message": rollback_obj, "success": True, "status_code": 200}

            )

    def test_quantity_checking(self):
        self.assertEqual(
            quantity_checking(10, 10, 15),
            False
        )
        self.assertEqual(
            quantity_checking(10, 15, 15),
            False
        )
        self.assertEqual(
            quantity_checking(15, 10, 15),
            False
        )
        self.assertEqual(
            quantity_checking(10, 10, 10),
            True
        )
#
    def test_create_rollback(self):
        qty_object = {

            "orderNumber": 11,
            "storageId": "2",
            "systemCode": "123",
            "count": 5,
            "staffId": 54545,
            "staffName": "dalam",
            "imeis": ["1", "2", "3", "4", "5"],
            'customerType': 'B2B',
        }
        self.assertEqual(
            create_rollback(
                11,
                "2",
                "123",
                5,
                54545,
                "dalam",
                ["1", "2", "3", "4", "5"],
                'B2B',
            ),
            qty_object
        )

    def test_checking_imeis(self):
        self.insert_initial_data()
        with self.mongo_mock:

            rollback_list1 = [
                {

                    "orderNumber": 11,
                    "storageId": "1",
                    "systemCode": "12345",
                    "count": 5,
                    "staffId": 54545,
                    "staffName": "dalam",
                    "imeis": ["1", "15", "3", "4", "5"]
                },
                {

                    "orderNumber": 11,
                    "storageId": "1",
                    "systemCode": "678910",
                    "count": 5,
                    "staffId": 54545,
                    "staffName": "dalam",
                    "imeis": ["5", "7", "8", "9", "10"]
                }
            ]

            self.assertEqual(
                imeis_checking(rollback_list1),
                False
            )

            rollback_list2 = [
                {

                    "orderNumber": 11,
                    "storageId": "1",
                    "systemCode": "12345",
                    "count": 5,
                    "staffId": 54545,
                    "staffName": "dalam",
                    "imeis": ["1", "2", "3", "4", "5"]
                },
                {

                    "orderNumber": 11,
                    "storageId": "1",
                    "systemCode": "678910111",
                    "count": 5,
                    "staffId": 54545,
                    "staffName": "dalam",
                    "imeis": ["5", "7", "8", "9", "10"]
                }
            ]

            self.assertEqual(
                imeis_checking(rollback_list2),
                False
            )
            rollback_list3 = [
                {

                    "orderNumber": 11,
                    "storageId": "1",
                    "systemCode": "12345",
                    "count": 5,
                    "staffId": 54545,
                    "staffName": "dalam",
                    "imeis": ["1", "2", "3", "4", "5"]
                },
                {

                    "orderNumber": 11,
                    "storageId": "1",
                    "systemCode": "678910",
                    "count": 5,
                    "staffId": 54545,
                    "staffName": "dalam",
                    "imeis": ["6", "7", "8", "9", "10"]
                }
            ]

            self.assertEqual(
                imeis_checking(rollback_list3),
                True
            )
    #
    def test_update_imeis(self):
        self.insert_initial_data()
        with self.mongo_mock:
            rollback_list1 = [
                {

                    "orderNumber": 11,
                    "storageId": "1",
                    "systemCode": "12345",
                    "count": 5,
                    "staffId": 54545,
                    "staffName": "dalam",
                    "imeis": ["1", "2", "3", "4", "5"],
                    "customer_type":"B2B"
                },
                {

                    "orderNumber": 11,
                    "storageId": "1",
                    "systemCode": "678910",
                    "count": 5,
                    "staffId": 54545,
                    "staffName": "dalam",
                    "imeis": ["6", "7", "8", "9", "10"],
                    "customer_type": "B2B"
                }
            ]

            rollback_list2 = [
                {

                    "orderNumber": 11,
                    "storageId": "1",
                    "systemCode": "12345",
                    "count": 5,
                    "staffId": 54545,
                    "staffName": "dalam",
                    "imeis": ["1", "2", "3", "4", "5"],
                    "customer_type": "B2B"
                },
                {

                    "orderNumber": 11,
                    "storageId": "1",
                    "systemCode": "678910",
                    "count": 5,
                    "staffId": 54545,
                    "staffName": "dalam",
                    "imeis": ["6", "7", "8", "91", "10"],
                    "customer_type": "B2B"
                }
            ]

            self.assertEqual(
                update_imeis(rollback_list1),
                True
            )

            self.assertEqual(
                update_imeis(rollback_list2),
                False
            )

