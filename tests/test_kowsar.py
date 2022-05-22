from unittest import mock, TestCase

import fakeredis
import mongomock

from app.controllers.kowsar_controller import get_kowsar, get_kowsar_items, update_kowsar_collection
from app.helpers.mongo_connection import MongoConnection
from app.helpers.redis_connection import RedisConnection


class KowsarTestCase(TestCase):

    def setUp(self):
        self.mongo_mock = mock.patch.object(MongoConnection, "client", new=mongomock.MongoClient())
        self.redis_mock = mock.patch.object(RedisConnection, "client",
                                            new=fakeredis.FakeStrictRedis(decode_responses=True))
        with self.mongo_mock, self.redis_mock:
            self.update_kowsar_collection = update_kowsar_collection()

    def test_update_kowsar_collection(self):
        self.assertEqual(self.update_kowsar_collection,
                         {"success": True, "message": "با موفقیت به روز رسانی شد", "status_code": 200})

    def test_get_kowsar(self):
        with self.mongo_mock, self.redis_mock:
            response = get_kowsar("1001")
            self.assertEqual(response, {'message': {'main_category': 'Device',
                                                    'sub_category': 'Mobile',
                                                    'system_code': '1001'},
                                        'status_code': 200,
                                        'success': True})
            second_response = get_kowsar("1009")
            self.assertEqual(second_response,
                             {"success": False, "status_code": 404, "error": "کالای مورد نظر یافت نشد"})

    def test_get_kowsar_items(self):
        with self.mongo_mock, self.redis_mock:
            response = get_kowsar_items("00")
            self.assertEqual(response, {'message': [{'label': 'Device', 'system_code': '10'},
                                                    {'label': 'Component', 'system_code': '11'},
                                                    {'label': 'Accessory', 'system_code': '12'},
                                                    {'label': 'Network', 'system_code': '13'},
                                                    {'label': 'Office Machines', 'system_code': '14'}],
                                        'status_code': 200,
                                        'success': True})
            second_response = get_kowsar_items("99")
            self.assertEqual(second_response,
                             {"success": False, "status_code": 404, "error": "کالای مورد نظر یافت نشد"})
