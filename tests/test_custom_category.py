from app.models.custom_category import CustomCategory
from app.models.product import Product


def test_add_product(delete_product_from_custom_category):
    data = {
        "system_code": "100111001002",
        "main_category": "Device",
        "sub_category": "Mobile",
        "brand": "Mobile G Plus",
        "model": "Q10",
        "config": {
            "storage": "32gb",
            "color": "blue",
            "guarantee": "sherkati",
            "ram": "3gb"
        },
        "attributes": {}
    }
    product = Product(**data)
    product.create()
    category = CustomCategory(**{"name": "atish bazi"})
    category.add_product(product.dict())
    assert category.get_products() == [{'attributes': {},
                                        'brand': 'Mobile G Plus',
                                        'config': {'color': 'blue',
                                                   'guarantee': 'sherkati',
                                                   'ram': '3gb',
                                                   'storage': '32gb'},
                                        'main_category': 'Device',
                                        'model': 'Q10',
                                        'sub_category': 'Mobile',
                                        'system_code': '100111001002'}]


def test_remove_product(add_product_to_custom_category):
    category = CustomCategory(**{"name": "atish bazi"})
    product = Product(**{
        "system_code": "100111001002",
        "main_category": "Device",
        "sub_category": "Mobile",
        "brand": "Mobile G Plus",
        "model": "Q10",
        "config": {
            "storage": "32gb",
            "color": "blue",
            "guarantee": "sherkati",
            "ram": "3gb"
        },
        "attributes": {
        }
    })
    category.remove_product(product.dict())
    assert category.get_products() == []


def test_get_products(add_and_remove_product_from_category):
    category = CustomCategory(**{"name": "atish bazi"})
    assert category.get_products() == [{'attributes': {},
                                        'brand': 'Mobile G Plus',
                                        'config': {'color': 'blue',
                                                   'guarantee': 'sherkati',
                                                   'ram': '3gb',
                                                   'storage': '32gb'},
                                        'main_category': 'Device',
                                        'model': 'Q10',
                                        'sub_category': 'Mobile',
                                        'system_code': '100111001002'}]


def test_get_custom_categories():
    category = CustomCategory(**{"name": "atish bazi"})
    category.get_custom_categories()
    assert category.get_custom_categories() == ['atish bazi']


def test_update_product_from_custom_category(add_and_remove_product_from_category):
    product = Product(**{
        "system_code": "100111001002",
        "main_category": "Device",
        "sub_category": "Mobile",
        "brand": "Mobile G Plus",
        "model": "Q10",
        "config": {
            "storage": "32gb",
            "color": "blue",
            "guarantee": "sherkati",
            "ram": "3gb"
        },
        "attributes": {
        }
    })
    category = CustomCategory(**{"name": "atish bazi"})
    category.update_product_from_custom_category(product.dict())
    assert category.get_products() == [{'attributes': {},
                                        'brand': 'Mobile G Plus',
                                        'config': {'color': 'blue',
                                                   'guarantee': 'sherkati',
                                                   'ram': '3gb',
                                                   'storage': '32gb'},
                                        'main_category': 'Device',
                                        'model': 'Q10',
                                        'sub_category': 'Mobile',
                                        'system_code': '100111001002'}]
