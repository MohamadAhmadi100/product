import sys

sys.path.append("..")

from test.helpers import Helpers
from source.models import Product


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
         'config': {'storage': '64gb', 'color': 'black', 'guarantee': 'sherkati', 'ram': '3gb'}, 'model': 'A022',
         'brand': 'Mobile Sumsung', 'sub_category': 'Mobile',
         'main_category': 'Device'},
        {'system_code': '100101030002',
         'config': {'storage': '64gb', 'color': 'blue', 'guarantee': 'sherkati', 'ram': '3gb'}, 'model': 'A022',
         'brand': 'Mobile Sumsung', 'sub_category': 'Mobile',
         'main_category': 'Device'},
        {'system_code': '100101030003',
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
    postfix = "/item/" + "?system_code=100101030001"
    data = ""
    response = Helpers.post_method_json(postfix=postfix, data=data).json()
    system_code = response.get("system_code")
    assert system_code is not None
    product = Product()
    product.delete_product(system_code=system_code)
