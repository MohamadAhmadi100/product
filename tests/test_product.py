from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_main_page(create_and_delete_multiple_attributes):
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == [
        {'name': 'test_1', 'label': 'قیمت', 'input_type': "Price", 'required': False, 'use_in_filter': True,
         'use_for_sort': True, 'parent': '1001', 'default_value': 0, 'values': None, 'set_to_nodes': True},
        {'name': 'test_2', 'label': 'قیمت', 'input_type': "Price", 'required': False, 'use_in_filter': True,
         'use_for_sort': True, 'parent': '1001', 'default_value': 0, 'values': None, 'set_to_nodes': True},
        {'name': 'test_3', 'label': 'قیمت', 'input_type': "Price", 'required': False, 'use_in_filter': True,
         'use_for_sort': True, 'parent': '1001', 'default_value': 0, 'values': None, 'set_to_nodes': True}
    ]


def test_add_attribute(delete_attribute):
    response = client.post("/api/v1/attr/", json={'name': 'price', 'label': 'قیمت', 'input_type': 8, 'required': False,
                                           'use_in_filter': True,
                                           'use_for_sort': True, 'parent': '1001', 'default_value': 0, 'values': None,
                                           'set_to_nodes': True})
    assert response.status_code == 201
    assert response.json() == {'message': 'attribute created successfully'}


def test_get_attributes(create_and_delete_multiple_attributes):
    response = client.get("/api/v1/attrs/1")
    assert response.status_code == 200
    assert response.json() == [
        {'name': 'test_1', 'label': 'قیمت', 'input_type': "Price", 'required': False, 'use_in_filter': True,
         'use_for_sort': True, 'parent': '1001', 'default_value': 0, 'values': None, 'set_to_nodes': True},
        {'name': 'test_2', 'label': 'قیمت', 'input_type': "Price", 'required': False, 'use_in_filter': True,
         'use_for_sort': True, 'parent': '1001', 'default_value': 0, 'values': None, 'set_to_nodes': True},
        {'name': 'test_3', 'label': 'قیمت', 'input_type': "Price", 'required': False, 'use_in_filter': True,
         'use_for_sort': True, 'parent': '1001', 'default_value': 0, 'values': None, 'set_to_nodes': True}
    ]


def test_get_attribute_by_name(create_and_delete_attribute):
    response = client.get("/api/v1/attr/" + "price")
    assert response.status_code == 200
    assert response.json() == {'name': 'price', 'label': 'قیمت', 'input_type': "Price", 'required': False,
                               'use_in_filter': True,
                               'use_for_sort': True, 'parent': '1001', 'default_value': 0, 'values': None,
                               'set_to_nodes': True}


def test_update_attribute(create_and_delete_attribute):
    response = client.put("/api/v1/attr/" + "price",
                          json={'name': 'price', 'label': 'قیمت', 'input_type': 8, 'required': False,
                                'use_in_filter': True,
                                'use_for_sort': True, 'parent': '1001', 'default_value': 0, 'values': None,
                                'set_to_nodes': False})
    assert response.status_code == 202
    assert response.json() == {'message': 'attribute updated successfully'}


def test_delete_attribute(create_attribute):
    response = client.delete("/api/v1/attr/" + "price")
    assert response.status_code == 200
    assert response.json() == {"message": "attribute deleted successfully"}
