from product.tests.helpers import Helpers
from product.database.models import Product


def test_get_product_api(create_and_delete_product_fixture):
    data = Helpers.get_url_json(postfix="/item/" + '100101030001')
    assert type(data) == dict
    assert data == {
        'system_code': '100101030001',
        'config':
            {
                'storage': '64gb',
                'color': 'black',
                'guarantee': 'sherkati',
                'ram': '3gb'
            },
        'image': 'src/default.png',
        'brand': 'Mobile Sumsung',
        'sub_category': 'Mobile',
        'main_category': 'Device',
        'model': 'A022'
    }


def test_get_all_products_api(create_and_delete_products_fixture):
    page_num = 1
    data = Helpers.get_url_json(postfix="/" + str(page_num))
    assert type(data) == list
    assert len(data) == 3
    assert type(data[0]) == dict
    sample_data = [
        {'system_code': '100101030001',
         'image': 'src/default.png',
         'config': {'storage': '64gb', 'color': 'black', 'guarantee': 'sherkati', 'ram': '3gb'}, 'model': 'A022',
         'brand': 'Mobile Sumsung', 'sub_category': 'Mobile',
         'main_category': 'Device'},
        {'system_code': '100101030002',
         'image': 'src/default.png',
         'config': {'storage': '64gb', 'color': 'blue', 'guarantee': 'sherkati', 'ram': '3gb'}, 'model': 'A022',
         'brand': 'Mobile Sumsung', 'sub_category': 'Mobile',
         'main_category': 'Device'},
        {'system_code': '100101030003',
         'image': 'src/default.png',
         'config': {'storage': '64gb', 'color': 'white', 'guarantee': 'sherkati', 'ram': '3gb'}, 'model': 'A022',
         'brand': 'Mobile Sumsung', 'sub_category': 'Mobile',
         'main_category': 'Device'}
    ]
    assert data == sample_data
    for i in range(0, 3):
        assert data[i] == sample_data[i]


def test_delete_product(create_product_fixture):
    Helpers.delete_method_json(postfix="/item/" + "100101030001")
    assert create_product_fixture.get_product(system_code="100101030001") is None


def test_create_product_api():
    postfix = "/item/"
    data = '{"system_code": "100101030001", "specification": {"image": "src/default.png"}}'
    response = Helpers.post_method_json(postfix=postfix, data=data).json()
    system_code = response.get("system_code")
    assert system_code is not None
    product = Product()
    product.delete_product(system_code=system_code)


def test_get_attr():
    data = Helpers.get_url_json(postfix="/item/attr/" + "100101030001")
    assert type(data) == list
    assert data == [{'category': 'model',
                     'default_value': '/src/default.png',
                     'is_required': 'False',
                     'name': 'image',
                     'sub_category': '',
                     'type': 'str',
                     'value': ['']}]


def test_set_attr():
    postfix = '/item/attr/'
    data = '''{
        "category": "model",
        "sub_category": "",
        "name": "price",
        "type": "int",
        "is_required": "True",
        "default_value": "0",
        "values": [
            ""
        ]
    }'''
    response = Helpers.post_method_json(postfix=postfix, data=data)
    assert response.status_code == 200


def test_get_kowsar():
    data = Helpers.get_url_json(postfix="/kowsar/" + "100101030001")
    assert type(data) == dict
    assert data == {'brand': 'Mobile Sumsung',
                    'config':
                        {'color': 'black',
                        'guarantee': 'sherkati',
                        'ram': '3gb',
                        'storage': '64gb'},
                    'main_category': 'Device',
                    'model': 'A022',
                    'sub_category': 'Mobile',
                    'system_code': '100101030001'}


def test_get_kowsar_items():
    data = Helpers.get_url_json(postfix="/kowsar/items/" + "10")
    assert type(data) == list
    assert data == [{'main_category': 'Device', 'sub_category': 'Mobile', 'system_code': '1001'},
                    {'main_category': 'Device', 'sub_category': 'Tablet', 'system_code': '1002'},
                    {'main_category': 'Device', 'sub_category': 'Notebook', 'system_code': '1003'},
                    {'main_category': 'Device', 'sub_category': 'All in One', 'system_code': '1004'},
                    {'main_category': 'Device', 'sub_category': 'PC', 'system_code': '1005'},
                    {'main_category': 'Device', 'sub_category': 'Server', 'system_code': '1006'},
                    {'main_category': 'Device', 'sub_category': 'Game Console', 'system_code': '1007'},
                    {'main_category': 'Device', 'sub_category': 'Camera', 'system_code': '1008'}]