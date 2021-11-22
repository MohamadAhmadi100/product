import sys

sys.path.append("..")

import pytest


def test_create_product(create_and_delete_product_fixture):
    assert create_and_delete_product_fixture.get_product(system_code='100101030001') is not None
    assert type(create_and_delete_product_fixture.get_product(system_code='100101030001')) == dict
    sample_product = create_and_delete_product_fixture.get_product(system_code='100101030001')
    assert sample_product == {
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
        'model': 'A022 '
    }


def test_delete_product(create_product_fixture):
    create_product_fixture.delete_product(system_code='100101030001')
    assert create_product_fixture.get_product(system_code='100101030001') is None


def test_get_product(create_and_delete_product_fixture):
    data = create_and_delete_product_fixture.get_product(system_code='100101030001')
    assert type(data) == dict
    assert data == {'system_code': '100101030001',
                    'config': {'storage': '64gb', 'color': 'black', 'guarantee': 'sherkati', 'ram': '3gb'},
                    'model': 'A022 ',
                    'brand': 'Mobile Sumsung', 'sub_category': 'Mobile',
                    'main_category': 'Device'}


def test_get_all_products(create_and_delete_products_fixture):
    data = create_and_delete_products_fixture.get_all_products(page=1, product_count=3)
    assert type(data) == list
    assert len(data) == 3
    assert type(data[0]) == dict
    sample_data = [
        {'system_code': '100101030001',
         'config': {'storage': '64gb', 'color': 'black', 'guarantee': 'sherkati', 'ram': '3gb'}, 'model': 'A022 ',
         'brand': 'Mobile Sumsung', 'sub_category': 'Mobile',
         'main_category': 'Device'},
        {'system_code': '100101030002',
         'config': {'storage': '64gb', 'color': 'blue', 'guarantee': 'sherkati', 'ram': '3gb'}, 'model': 'A022 ',
         'brand': 'Mobile Sumsung', 'sub_category': 'Mobile',
         'main_category': 'Device'},
        {'system_code': '100101030003',
         'config': {'storage': '64gb', 'color': 'white', 'guarantee': 'sherkati', 'ram': '3gb'}, 'model': 'A022 ',
         'brand': 'Mobile Sumsung', 'sub_category': 'Mobile',
         'main_category': 'Device'}
    ]
    for i in range(0, 3):
        assert data[i] == sample_data[i]
