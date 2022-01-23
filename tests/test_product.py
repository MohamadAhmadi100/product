from app.models.product import Product
from tests.conftest import delete_parent


def test_add_parent():
    sample_data = {
        "system_code": "100104021",
        "name": "ردمی 9c"
    }
    product = Product(**sample_data)
    product.create()
    assert product.get('100104021') == [{'attributes': {},
                                         'brand': 'Mobile Xiaomi',
                                         'config': None,
                                         'maincategory': 'Device',
                                         'model': 'Xiaomi Redmi 9c',
                                         'name': 'ردمی 9c',
                                         'subcategory': 'Mobile',
                                         'system_code': '100104021'}]
    delete_parent()


def test_create_child(create_parent):
    sample_data = {
        "system_code": "100104021006"
    }
    product = Product(**sample_data)
    product.create_child()
    assert product.get("100104021") == [{'attributes': {},
                                         'brand': 'Mobile Xiaomi',
                                         'config': None,
                                         'maincategory': 'Device',
                                         'model': 'Xiaomi Redmi 9c',
                                         'name': 'ردمی 9c',
                                         'products': [{'attributes': {},
                                                       'brand': 'Mobile Xiaomi',
                                                       'config': {'color': 'orange',
                                                                  'guarantee': 'sherkati',
                                                                  'storage': '64'},
                                                       'maincategory': 'Device',
                                                       'model': 'Xiaomi Redmi 9c',
                                                       'name': '',
                                                       'subcategory': 'Mobile',
                                                       'system_code': '100104021006'}],
                                         'subcategory': 'Mobile',
                                         'system_code': '100104021'}]
    delete_parent()


def test_add_attribute(create_child):
    sample_data = {
        "system_code": "100104021006",
        "attributes": {
            "image": "/src/default.jpg",
            "year": 2020
        }
    }
    product = Product(**sample_data)
    product.add_attributes()
    assert product.get('100104021') == [{'attributes': {},
                                         'brand': 'Mobile Xiaomi',
                                         'config': None,
                                         'maincategory': 'Device',
                                         'model': 'Xiaomi Redmi 9c',
                                         'name': 'ردمی 9c',
                                         'products': [{'attributes': {'image': '/src/default.jpg', 'year': 2020},
                                                       'brand': 'Mobile Xiaomi',
                                                       'config': {'color': 'orange',
                                                                  'guarantee': 'sherkati',
                                                                  'storage': '64'},
                                                       'maincategory': 'Device',
                                                       'model': 'Xiaomi Redmi 9c',
                                                       'name': '',
                                                       'subcategory': 'Mobile',
                                                       'system_code': '100104021006'}],
                                         'subcategory': 'Mobile',
                                         'system_code': '100104021'}]
    delete_parent()


def test_get_parent(create_child):
    product = Product.construct()
    assert product.get() == ({'page': 1, 'per_page': 10, 'total_counts': 1},
                             [{'attributes': {},
                               'brand': 'Mobile Xiaomi',
                               'config': None,
                               'maincategory': 'Device',
                               'model': 'Xiaomi Redmi 9c',
                               'name': 'ردمی 9c',
                               'products': [{'attributes': {},
                                             'brand': 'Mobile Xiaomi',
                                             'config': {'color': 'orange',
                                                        'guarantee': 'sherkati',
                                                        'storage': '64'},
                                             'maincategory': 'Device',
                                             'model': 'Xiaomi Redmi 9c',
                                             'name': '',
                                             'subcategory': 'Mobile',
                                             'system_code': '100104021006'}],
                               'subcategory': 'Mobile',
                               'system_code': '100104021'}])
    delete_parent()


def test_delete_parent(create_child):
    product = Product.construct()
    product.get('100104021')
    product.delete()
    assert Product.get('100104021') == []
