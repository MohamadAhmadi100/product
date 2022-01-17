from app.models.custom_category import CustomCategory
from app.models.product import Product


def test_add_product(delete_product_from_custom_category):
    data = {'attributes': {'image': '/src/default.jpg', 'year': 2020},
            'brand': 'Mobile Xiaomi',
            'config': {'color': 'orange', 'guarantee': 'sherkati', 'storage': '64'},
            'main_category': 'Device',
            'model': 'Xiaomi Redmi 9c',
            'sub_category': 'Mobile',
            'system_code': '100104021006'}
    product = Product(**data)
    product.create()
    category = CustomCategory(**{"name": "atish bazi"})
    category.add(product.dict())
    assert category.get_products() == [{'attributes': {'image': '/src/default.jpg', 'year': 2020},
                                        'brand': 'Mobile Xiaomi',
                                        'config': {'color': 'orange', 'guarantee': 'sherkati', 'storage': '64'},
                                        'main_category': 'Device',
                                        'model': 'Xiaomi Redmi 9c',
                                        'sub_category': 'Mobile',
                                        'system_code': '100104021006'}]


def test_remove_product(add_product_to_custom_category):
    category = CustomCategory(**{"name": "atish bazi"})
    product = Product(**{'attributes': {'image': '/src/default.jpg', 'year': 2020},
                         'brand': 'Mobile Xiaomi',
                         'config': {'color': 'orange', 'guarantee': 'sherkati', 'storage': '64'},
                         'main_category': 'Device',
                         'model': 'Xiaomi Redmi 9c',
                         'sub_category': 'Mobile',
                         'system_code': '100104021006'})
    category.remove(product.dict())
    assert category.get_products() == []


def test_get_products(add_and_remove_product_from_category):
    category = CustomCategory(**{"name": "atish bazi"})
    assert category.get_products() == [{'attributes': {'image': '/src/default.jpg', 'year': 2020},
                                        'brand': 'Mobile Xiaomi',
                                        'config': {'color': 'orange', 'guarantee': 'sherkati', 'storage': '64'},
                                        'main_category': 'Device',
                                        'model': 'Xiaomi Redmi 9c',
                                        'sub_category': 'Mobile',
                                        'system_code': '100104021006'}]


def test_get_custom_categories():
    category = CustomCategory(**{"name": "atish bazi"})
    category.get_custom_categories()
    assert category.get_custom_categories() == ['atish bazi']


def test_update_product_from_custom_category(add_and_remove_product_from_category):
    product = Product(**{'attributes': {'image': '/src/default.jpg', 'year': 2020},
                         'brand': 'Mobile Xiaomi',
                         'config': {'color': 'orange', 'guarantee': 'sherkati', 'storage': '64'},
                         'main_category': 'Device',
                         'model': 'Xiaomi Redmi 9c',
                         'sub_category': 'Mobile',
                         'system_code': '100104021006'})
    category = CustomCategory(**{"name": "atish bazi"})
    category.update_product_from_custom_category(product.dict())
    assert category.get_products() == [{'attributes': {'image': '/src/default.jpg', 'year': 2020},
                                        'brand': 'Mobile Xiaomi',
                                        'config': {'color': 'orange', 'guarantee': 'sherkati', 'storage': '64'},
                                        'main_category': 'Device',
                                        'model': 'Xiaomi Redmi 9c',
                                        'sub_category': 'Mobile',
                                        'system_code': '100104021006'}]
