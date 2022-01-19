from fastapi.testclient import TestClient

from app.main import app
from tests.conftest import delete_parent, delete_product

client = TestClient(app)


def test_create_parent():
    response = client.post("/api/v1/product/parent/", json={
        "system_code": "100104021",
        "name": "ردمی 9c"
    })
    assert response.status_code == 201
    assert response.json() == {'label': 'محصول با موفقیت ساخته شد', 'message': 'product created successfully'}
    delete_parent()


def test_get_parent(create_and_delete_parent):
    response = client.get("/api/v1/product/" + "100104021")
    assert response.status_code == 200
    assert response.json() == [{'attributes': {},
                                'brand': 'Mobile Xiaomi',
                                'config': None,
                                'maincategory': 'Device',
                                'model': 'Xiaomi Redmi 9c',
                                'name': 'ردمی 9c',
                                'step': 1,
                                'subcategory': 'Mobile',
                                'system_code': '100104021'}]


def test_create_child(create_and_delete_parent):
    response = client.post("/api/v1/product/child/", json={
        "system_codes": [
            "100104021006"
        ]
    })
    assert response.status_code == 201
    assert response.json() == {'label': 'محصول با موفقیت ساخته شد', 'message': 'product created successfully'}
    delete_product()


def test_get_child():
    response = client.get("/api/v1/product/child/")
    assert response.status_code == 200
    assert response.json() == {'system_code': {'isRequired': True,
                                               'maxLength': 12,
                                               'minLength': 12,
                                               'placeholder': '100104021006',
                                               'title': 'کد سیستمی',
                                               'type': 'string'}}
    delete_parent()


def test_add_attributes(create_child): #error
    response = client.post("/api/v1/product/attributes/", json={
        "system_code": "100104021006",
        "attributes": {
            "image": "/src/default.jpg",
            "year": 2020
        }
    })
    assert response.status_code == 201
    assert response.json() == []


def test_get_attributes():#error
    response = client.get("/api/v1/product/child/")
    assert response.status_code == 200
    assert response.json() == {'system_code': {'isRequired': True,
                                               'maxLength': 12,
                                               'minLength': 12,
                                               'placeholder': '100104021006',
                                               'title': 'کد سیستمی',
                                               'type': 'string'}}


def test_get_all_product():#error
    response = client.get('api/v1//products/1')
    assert response.status_code == 200
    assert response.json() == {'data': [], 'headers': {'page': 1, 'per_page': 10, 'total_counts': 0}}


def test_delete_product(create_product):#error
    response = client.delete('/api/v1/product/' + '')
    assert response.status_code == 200
    assert response.json() == []
