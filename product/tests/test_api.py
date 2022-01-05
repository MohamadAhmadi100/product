import requests
from product.database.models import Product, Assignees


def test_create_product():
    data = '''{
            "system_code": "100101030001",
            "specification": {"color":"green","price":2000,"year":1988, "size":200,"image":"png"}
        }'''
    url = "http://127.0.0.1:8000/item"
    response = requests.post(url, data=data)
    assert response.status_code == 201
    Product.delete_product('100101030001')


def test_read_products(create_and_delete_products_fixture):
    response = requests.get('http://127.0.0.1:8000/1')
    data = Product.get_all_products(1, 3)
    assert type(data) == list
    assert len(data) == 3
    assert type(data[0])
    assert response.status_code == 200


def test_read_product(create_and_delete_product_fixture):
    response = requests.get('http://127.0.0.1:8000/item/' + '100101030001')
    data = Product.get_product('100101030001')
    print(data)
    assert response.status_code == 200
    assert data == {'system_code': '100101030001',
                    'config': {'storage': '64gb', 'color': 'black', 'guarantee': 'sherkati', 'ram': '3gb'},
                    'model': 'A022', 'brand': 'Mobile Sumsung', 'sub_category': 'Mobile', 'main_category': 'Device',
                    'image': 'src/default.png'}


def test_delete_product(create_product_fixture):
    response = requests.delete('http://127.0.0.1:8000/item/' + '100101030001')
    assert response.status_code == 204
    data = Product.get_product('100101030001')
    assert data is None


def test_update_product(create_and_delete_product_fixture):
    data = '''{
        "system_code": "100101030001",
        "specification": {"color":"green","price":2000,"year":1988, "size":200,"image":"png"}
    }'''
    response = requests.put('http://127.0.0.1:8000/item/' + '100101030001', data=data)
    assert response.status_code == 202


def test_get_kowsar(create_and_delete_product_fixture):
    response = requests.get('http://127.0.0.1:8000/kowsar/' + '100101030001')
    assert response.status_code == 200


def test_get_kowsar_items(create_and_delete_product_fixture):
    response = requests.get('http://127.0.0.1:8000/kowsar/items' + '100101030001')
    assert response.status_code == 200


def test_update_product_by_set_to_nodes():
    response = requests.get('http://127.0.0.1:8000/attribute_by_kowsar/')
    assert response.status_code == 200


def test_get_all_attributes():
    response = requests.get('http://127.0.0.1:8000/attributes/')
    assert response.status_code == 200


def test_get_all_attribute_by_system_code():
    response = requests.get('http://127.0.0.1:8000/attributes/' + '100101030001')
    assert response.status_code == 200

# # from product.database.models import Product
# from fastapi.testclient import TestClient
# from product.main import app
#
# client = TestClient(app)
#
#
# def test_create_product(delete_product):
#     response = client.post("/item", json={
#         "system_code": "100104021006",
#         "specification": {"color": "green", "transfer_type": true, "guarantee": "abcd", "size": 200}
#     })
#     assert response.status_code == 201
#     assert response.json() == {"system_code": "100104021006"}
#
#
# def test_get_kowsar():
#     pass
#
#
# def test_get_kowsar_items():
#     pass
#
#
# def test_read_products(create_and_delete_products_fixture):
#     page_num = 1
#     response = client.get("/" + page_num)
#     assert response.status_code == 200
#
#
# def test_read_product(create_and_delete_product_fixture):
#     response = client.get('/item/' + '100101030001')
#     assert response.status_code == 200
#
#
# def test_delete_product(create_product_fixture):
#     response = client.delete('/item/' + '100101030001')
#     assert response.status_code == 200
#
#
# def test_update_product_by_set_to_nodes():
#     response = client.get("/attribute_by_kowsar/")
#     assert response.status_code == 200
#
#
# def test_get_all_attribute():
#     response = client.get("/attribute/")
#     assert response.status_code == 200
#
#
# def test_get_all_attribute_by_system_code():
#     response = client.get("/attributes/" + '100104021006')
#     assert response.status_code == 200

# def test_get_product_api(create_and_delete_product_fixture):
#     data = Helpers.get_url_json(postfix="/item/" + '100101030001')
#
#     assert type(data) == dict
#     print(data)
#     assert data == {'system_code': '100101030001',
#                     'config': {'storage': '64gb', 'color': 'black', 'guarantee': 'sherkati', 'ram': '3gb'},
#                     'model': 'A022',
#                     'brand': 'Mobile Sumsung', 'sub_category': 'Mobile', 'main_category': 'Device'}
#
#
# def test_get_all_products_api(create_and_delete_products_fixture):
#     page_num = 1
#     data = Helpers.get_url_json(postfix="/" + str(page_num))
#     assert type(data) == list
#     assert len(data) == 3
#     assert type(data[0]) == dict
#     sample_data = [
#         {'system_code': '100104021006', 'config': {'color': 'orange', 'guarantee': 'sherkati', 'storage': '64'},
#          'model': 'Xiaomi Redmi 9c', 'brand': 'Mobile Xiaomi', 'sub_category': 'Mobile', 'main_category': 'Device',
#          'color': 'green', 'transfer_type': True, 'guarantee': ''}, {'system_code': '100105015003',
#                                                                      'config': {'storage': '128gb',
#                                                                                 'color': 'breathing crystal',
#                                                                                 'guarantee': 'sherkati'},
#                                                                      'model': 'Y8p', 'brand': 'Mobile Huawei',
#                                                                      'sub_category': 'Mobile',
#                                                                      'main_category': 'Device', 'color': 'green',
#                                                                      'transfer_type': True, 'guarantee': '',
#                                                                      'size': 200},
#         {'system_code': '120301001001', 'config': {'color': 'color', 'guarantee': 'life time', 'storage': '8'},
#          'model': 'Cruzer blade cz50', 'brand': 'Flash Memory SanDisk', 'sub_category': 'Flash Memory',
#          'main_category': 'Accessory', 'images': 200}]
#
#     assert data == sample_data
#     for i in range(0, 3):
#         assert data[i] == sample_data[i]
#
#
# def test_delete_product(create_product_fixture):
#     Helpers.delete_method_json(postfix="/item/" + "100101030001")
#     assert create_product_fixture.get_product(system_code="100101030001") is None
#
#
# def test_create_product_api():
#     postfix = "/item/"
#     data = '{"system_code": "100101030001", "specification": {"image": "src/default.png"}}'
#     response = Helpers.post_method_json(postfix=postfix, data=data).json()
#     system_code = response.get("system_code")
#     assert system_code is not None
#     product = Product()
#     product.delete_product(system_code=system_code)
#
#
# def test_get_attr():
#     data = Helpers.get_url_json(postfix="/item/attr/" + "100101030001")
#     print(data)
#     assert type(data) == dict
#     assert data == [{'category': 'model',
#                      'default_value': '/src/default.png',
#                      'is_required': 'False',
#                      'name': 'image',
#                      'sub_category': '',
#                      'type': 'str',
#                      'value': ['']}]
#
#
# def test_get_kowsar():
#     data = Helpers.get_url_json(postfix="/kowsar/" + "100101030001")
#     print(data)
#     assert type(data) == dict
#     assert data == {'system_code': '100101030001',
#                     'config': {'storage': '64gb', 'color': 'black', 'guarantee': 'sherkati', 'ram': '3gb'},
#                     'model': 'A022', 'brand': 'Mobile Sumsung', 'sub_category': 'Mobile', 'main_category': 'Device',
#                     'attributes': {}}
#
#
# def test_get_kowsar_items():
#     data = Helpers.get_url_json(postfix="/kowsar/items/" + "10")
#     assert type(data) == list
#     assert data == [{'main_category': 'Device', 'sub_category': 'Mobile', 'system_code': '1001'},
#                     {'main_category': 'Device', 'sub_category': 'Tablet', 'system_code': '1002'},
#                     {'main_category': 'Device', 'sub_category': 'Notebook', 'system_code': '1003'},
#                     {'main_category': 'Device', 'sub_category': 'All in One', 'system_code': '1004'},
#                     {'main_category': 'Device', 'sub_category': 'PC', 'system_code': '1005'},
#                     {'main_category': 'Device', 'sub_category': 'Server', 'system_code': '1006'},
#                     {'main_category': 'Device', 'sub_category': 'Game Console', 'system_code': '1007'},
#                     {'main_category': 'Device', 'sub_category': 'Camera', 'system_code': '1008'}]
