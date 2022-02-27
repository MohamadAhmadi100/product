from app.controllers.kowsar_controller import get_kowsar, get_kowsar_items, update_kowsar_collection


def test_update_kowsar_collection():
    response = update_kowsar_collection()
    assert response == {"success": True, "message": "با موفقیت به روز رسانی شد", "status_code": 200}


def test_get_kowsar():
    response = get_kowsar("1001")
    assert response == {'message': {'attributes': [{'default_value': '/src/default.png',
                                                    'input_type': 'Media Image',
                                                    'label': 'عکس',
                                                    'name': 'image',
                                                    'parent': '1001',
                                                    'required': False,
                                                    'set_to_nodes': True,
                                                    'use_for_sort': False,
                                                    'use_in_filter': False,
                                                    'values': None}],
                                    'main_category': 'Device',
                                    'sub_category': 'Mobile',
                                    'system_code': '1001'},
                        'status_code': 200,
                        'success': True}
    second_response = get_kowsar("1009")
    assert second_response == {"success": False, "status_code": 404, "error": "کالای مورد نظر یافت نشد"}


def test_get_kowsar_items():
    response = get_kowsar_items("00")
    assert response == {'message': [{'label': 'Device', 'system_code': '10'},
                                    {'label': 'Component', 'system_code': '11'},
                                    {'label': 'Accessory', 'system_code': '12'},
                                    {'label': 'Network', 'system_code': '13'},
                                    {'label': 'Office Machines', 'system_code': '14'}],
                        'status_code': 200,
                        'success': True}
    second_response = get_kowsar_items("99")
    assert second_response == {"success": False, "status_code": 404, "error": "کالای مورد نظر یافت نشد"}
