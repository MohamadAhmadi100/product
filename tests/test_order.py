from app.helpers.mongo_connection import MongoConnection
from unittest import mock, TestCase
import jdatetime
import mongomock
from app.models.order import *
from app.controllers.order import exit_order_handler, exit_order


class OrderTest(TestCase):
    products = [
        {
            "system_code": "12345",
            "imeis": ["1", "2", "3", "4", "5"]

        },
        {
            "system_code": "678910",
            "imeis": ["6", "7", "8", "9", "10"]

        }
    ]
    products2 = [
        {
            "system_code": "12345",
            "imeis": ["1", "2", "3", "4", "5"]

        },
        {
            "system_code": "678910",
            "imeis": ["6", "545", "8", "9", "10"]

        }
    ]

    def test_exit_order(self):

        rollback_obj = [{

            "orderNumber": 111,
            "storageId": "50",
            "systemCode": "12345",
            "count": 5,
            "staffId": "1221",
            "staffName": "dalam",
            "imeis": ["1", "2", "3", "4", "5"]
        },
            {"orderNumber": 111,
             "storageId": "50",
             "systemCode": "678910",
             "count": 5,
             "staffId": "1221",
             "staffName": "dalam",
             "imeis": ["6", "7", "8", "9", "10"]
             }
        ]



        self.assertEqual(
            exit_order(111, "50", self.products2, "1221", "dalam"),
            {"message": "مشکل در چک imei", "success": False, "status_code": 417}
        )
        self.assertEqual(
            exit_order(111, "50", self.products, "1221", "dalam"),
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

    def test_create_rollback(self):
        qty_object = {

            "orderNumber": 11,
            "storageId": "2",
            "systemCode": "123",
            "count": 5,
            "staffId": 54545,
            "staffName": "dalam",
            "imeis": ["1", "2", "3", "4", "5"]
        }
        self.assertEqual(
            create_rollback(
                11,
                "2",
                "123",
                5,
                54545,
                "dalam",
                ["1", "2", "3", "4", "5"]
            ),
            qty_object
        )

    def test_checking_imeis(self):
        rollback_list1 = [
            {

                "orderNumber": 11,
                "storageId": "50",
                "systemCode": "12345",
                "count": 5,
                "staffId": 54545,
                "staffName": "dalam",
                "imeis": ["1", "15", "3", "4", "5"]
            },
            {

                "orderNumber": 11,
                "storageId": "50",
                "systemCode": "678910",
                "count": 5,
                "staffId": 54545,
                "staffName": "dalam",
                "imeis": ["5", "7", "8", "9", "10"]
            }
        ]

        self.assertEqual(
            checking_imeis(rollback_list1),
            False
        )

        rollback_list2 = [
            {

                "orderNumber": 11,
                "storageId": "50",
                "systemCode": "12345",
                "count": 5,
                "staffId": 54545,
                "staffName": "dalam",
                "imeis": ["1", "2", "3", "4", "5"]
            },
            {

                "orderNumber": 11,
                "storageId": "50",
                "systemCode": "678910111",
                "count": 5,
                "staffId": 54545,
                "staffName": "dalam",
                "imeis": ["5", "7", "8", "9", "10"]
            }
        ]

        self.assertEqual(
            checking_imeis(rollback_list2),
            False
        )
        rollback_list3 = [
            {

                "orderNumber": 11,
                "storageId": "50",
                "systemCode": "12345",
                "count": 5,
                "staffId": 54545,
                "staffName": "dalam",
                "imeis": ["1", "2", "3", "4", "5"]
            },
            {

                "orderNumber": 11,
                "storageId": "50",
                "systemCode": "678910",
                "count": 5,
                "staffId": 54545,
                "staffName": "dalam",
                "imeis": ["6", "7", "8", "9", "10"]
            }
        ]

        self.assertEqual(
            checking_imeis(rollback_list3),
            True

        )

    def test_update_imeis(self):
        rollback_list1 = [
            {

                "orderNumber": 11,
                "storageId": "50",
                "systemCode": "12345",
                "count": 5,
                "staffId": 54545,
                "staffName": "dalam",
                "imeis": ["1", "2", "3", "4", "5"]
            },
            {

                "orderNumber": 11,
                "storageId": "50",
                "systemCode": "678910",
                "count": 5,
                "staffId": 54545,
                "staffName": "dalam",
                "imeis": ["6", "7", "8", "9", "10"]
            }
        ]

        self.assertEqual(
            update_imeis(rollback_list1),
            True
        )

    def test_create_archive_obj(self):
        imeis = ["1", "2", "3"]
        imei_obj = [{"imei": "1"}, {"imei": "2"}, {"imei": "3"}]

        self.assertEqual(
            create_archive_obj(imeis),
            imei_obj
        )

        # rollback_list2 = [
        #     {
        #
        #         "orderNumber": 11,
        #         "storageId": "50",
        #         "systemCode": "12345",
        #         "count": 5,
        #         "staffId": 54545,
        #         "staffName": "dalam",
        #         "imeis": ["1", "2", "3", "4", "5"]
        #     },
        #     {
        #
        #         "orderNumber": 11,
        #         "storageId": "50",
        #         "systemCode": "678910",
        #         "count": 5,
        #         "staffId": 54545,
        #         "staffName": "dalam",
        #         "imeis": ["6", "7", "8", "9", "10"]
        #     }
        # ]
        #
        # self.assertEqual(
        #     update_imeis(rollback_list2),
        #     True
        # )
        #
        #
        #
        #
        #
