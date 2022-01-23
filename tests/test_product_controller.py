from fastapi.testclient import TestClient

from app.main import app
from tests.conftest import delete_parent

client = TestClient(app)


def test_create_parent_scheme():
    response = client.get("/api/v1/product/parent/")
    assert response.status_code == 200
    assert response.json() == {'name': {'isRequired': False,
                                        'maxLength': 256,
                                        'minLength': 3,
                                        'placeholder': 'ردمی ۹ سی',
                                        'title': 'نام',
                                        'type': 'string'},
                               'system_code': {'isRequired': True,
                                               'maxLength': 9,
                                               'minLength': 9,
                                               'placeholder': '100104021',
                                               'title': 'شناسه محصول',
                                               'type': 'string'}}


def test_create_parent():
    response = client.post("/api/v1/product/parent/", json={
        "system_code": "100104021",
        "name": "ردمی 9c"
    })
    assert response.status_code == 201
    assert response.json() == {'label': 'محصول با موفقیت ساخته شد', 'message': 'product created successfully'}
    delete_parent()


def test_create_child_schema():
    response = client.get("/api/v1/product/child/")
    assert response.status_code == 200
    assert response.json() == {'system_code': {'isRequired': True,
                                               'maxLength': 12,
                                               'minLength': 12,
                                               'placeholder': '100104021006',
                                               'title': 'شناسه محصول',
                                               'type': 'string'}}


def test_create_child(create_and_delete_parent):
    response = client.post("/api/v1/product/child/", json={
        "system_code": "100104021015"
    })
    assert response.status_code == 201
    assert response.json() == {'label': 'محصول با موفقیت ساخته شد', 'message': 'product created successfully'}
    delete_parent()


def test_add_attributes_schema():
    response = client.get("/api/v1/product/attributes/")
    assert response.status_code == 200
    assert response.json() == {'attributes': {'default': {},
                                              'isRequired': False,
                                              'maxLength': 256,
                                              'title': 'صفت ها',
                                              'type': 'object'},
                               'system_code': {'isRequired': True,
                                               'maxLength': 12,
                                               'minLength': 12,
                                               'placeholder': '100104021006',
                                               'title': 'کد سیستمی',
                                               'type': 'string'}}


def test_add_attributes(create_child):
    response = client.post("/api/v1/product/attributes/", json={
        "system_code": "100104021006",
        "attributes": {
            "image": "/src/default.jpg",
            "year": 2020
        }
    })
    assert response.status_code == 201
    assert response.json() == {'label': 'صفت با موفقیت اضافه شد', 'message': 'attribute added successfully'}
    delete_parent()


def test_get_all_products(create_and_delete_parent):
    response = client.get('/api/v1/products/1')
    assert response.status_code == 200
    assert response.json() == {'data': [{'attributes': {},
                                         'brand': 'Mobile Xiaomi',
                                         'config': None,
                                         'maincategory': 'Device',
                                         'model': 'Xiaomi Redmi 9c',
                                         'name': 'ردمی 9c',
                                         'subcategory': 'Mobile',
                                         'system_code': '100104021'}],
                               'headers': {'page': 1, 'per_page': 10, 'total_counts': 1}}


def test_get_product_by_system_code(create_and_delete_parent):
    response = client.get("/api/v1/product/100104021")
    assert response.status_code == 200
    assert response.json() == [{'attributes': {},
                                'brand': 'Mobile Xiaomi',
                                'config': None,
                                'maincategory': 'Device',
                                'model': 'Xiaomi Redmi 9c',
                                'name': 'ردمی 9c',
                                'subcategory': 'Mobile',
                                'system_code': '100104021'}]


def test_delete_product(add_attributes):  # error
    response = client.delete('/api/v1/product/' + '100104021006')
    assert response.status_code == 200
    assert response.json() == []


def test_update_attribute_collection():
    response = client.get("/api/v1/product/update_attribute_collection/")
    assert response.status_code == 200
    assert response.json() == {'label': 'جدول تنظیمات بروز شد', 'message': 'attribute collection updated'}


def test_suggest_product():
    response = client.get("/api/v1/product/100104021/items")
    assert response.status_code == 200
    assert response.json() == [{'label': {'color': 'gray',
                                          'guarantee': 'awat',
                                          'ram': '2gb',
                                          'storage': '32gb'},
                                'system_code': '100104021012'},
                               {'label': {'color': 'gray',
                                          'guarantee': 'sherkati 01',
                                          'ram': '3gb',
                                          'storage': '64gb'},
                                'system_code': '100104021015'},
                               {'label': {'color': 'blue', 'guarantee': 'sherkati', 'storage': '64'},
                                'system_code': '100104021007'},
                               {'label': {'color': 'blue', 'guarantee': 'sherkati', 'storage': '32'},
                                'system_code': '100104021001'},
                               {'label': {'color': 'gray',
                                          'guarantee': 'awat',
                                          'ram': '3gb',
                                          'storage': '64'},
                                'system_code': '100104021009'},
                               {'label': {'color': 'orange',
                                          'guarantee': 'awat',
                                          'ram': '3gb',
                                          'storage': '64'},
                                'system_code': '100104021010'},
                               {'label': {'color': 'blue',
                                          'guarantee': 'awat',
                                          'ram': '2gb',
                                          'storage': '32gb'},
                                'system_code': '100104021011'},
                               {'label': {'color': 'blue',
                                          'guarantee': 'awat',
                                          'ram': '3gb',
                                          'storage': '64'},
                                'system_code': '100104021008'},
                               {'label': {'color': 'orange',
                                          'guarantee': 'awat',
                                          'ram': '2gb',
                                          'storage': '32gb'},
                                'system_code': '100104021017'},
                               {'label': {'color': 'orange', 'guarantee': 'sherkati', 'storage': '32'},
                                'system_code': '100104021005'},
                               {'label': {'color': 'gray', 'guarantee': 'sherkati', 'storage': '64'},
                                'system_code': '100104021004'},
                               {'label': {'color': 'white',
                                          'guarantee': 'awat',
                                          'ram': '2gb',
                                          'storage': '32gb'},
                                'system_code': '100104021013'},
                               {'label': {'color': 'white',
                                          'guarantee': 'sherkati 01',
                                          'ram': '3gb',
                                          'storage': '64gb'},
                                'system_code': '100104021016'},
                               {'label': {'color': 'coral', 'guarantee': 'sherkati', 'storage': '32'},
                                'system_code': '100104021002'},
                               {'label': {'color': 'blue',
                                          'guarantee': 'sherkati 01',
                                          'ram': '3gb',
                                          'storage': '64gb'},
                                'system_code': '100104021014'},
                               {'label': {'color': 'gray', 'guarantee': 'sherkati', 'storage': '32'},
                                'system_code': '100104021003'},
                               {'label': {'color': 'orange', 'guarantee': 'sherkati', 'storage': '64'},
                                'system_code': '100104021006'}]
