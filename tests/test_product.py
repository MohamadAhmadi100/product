from app.models.product import Product
from tests.conftest import delete_parent, delete_product


def test_add_parent():
    sample_data = {
        "system_code": "100104021",
        "name": "ردمی 9c"
    }
    product = Product(**sample_data)
    product.step_setter(1)
    product.create()
    assert product.get('100104021') == [{'attributes': {},
                                         'brand': 'Mobile Xiaomi',
                                         'config': None,
                                         'maincategory': 'Device',
                                         'model': 'Xiaomi Redmi 9c',
                                         'name': 'ردمی 9c',
                                         'step': 1,
                                         'subcategory': 'Mobile',
                                         'system_code': '100104021'}]
    delete_parent()


def test_create_child(create_parent):
    sample_data = {
        "system_code": "100104021006"
    }
    product = Product(**sample_data)
    product.step_setter(2)
    product.create_child('100104021006')
    assert product.get("100104021006") == []
    delete_parent()


def test_add_attribute():
    sample_data = {
        "system_code": "100104021006",
        "attributes": {
            "image": "/src/default.jpg",
            "year": 2020
        }
    }
    product = Product(**sample_data)
    product.step_setter(1)
    product.add_attributes()
    assert product.get('100104021006') == []


def test_get_product(create_child):
    product = Product.construct()
    assert product.get() == ({'page': 1, 'per_page': 10, 'total_counts': 1},
                             [{'attributes': {},
                               'brand': 'Mobile Xiaomi',
                               'config': None,
                               'maincategory': 'Device',
                               'model': 'Xiaomi Redmi 9c',
                               'name': 'ردمی 9c',
                               'step': 2,
                               'subcategory': 'Mobile',
                               'system_code': '100104021'}])
    delete_parent()






