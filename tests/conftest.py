import pytest

from app.models.custom_category import CustomCategory
from app.models.product import Product


@pytest.fixture
def create_and_delete_product():
    sample_data = {
        "system_code": "120301001001",
        "specification": {
            "country": "iran"
        }
    }
    product = Product(**sample_data)
    product.create()
    yield product
    product.delete()


@pytest.fixture
def create_product():
    sample_data = {
        "system_code": "120301001001",
        "specification": {
            "country": "iran"
        }
    }
    product = Product(**sample_data)
    product.create()
    yield product


@pytest.fixture()
def create_and_delete_multiple_products():
    system_code_list = ['100201002002', '100101047003', '100101047003']
    for item in system_code_list:
        product = Product(**{
            "system_code": item,
            "specification": {
                "color": "green",
                "price": 200,
                "year": 2000,
                "size": 200,
                "image": "png",
                "full-HD": "full"
            }
        })
        product.create()
        yield
        for system_code in system_code_list:
            new_product = Product.construct()
            new_product.get(system_code)
            new_product.delete()


@pytest.fixture
def delete_product():
    yield
    product = Product.construct()
    product.get("system_code")
    product.delete()


@pytest.fixture
def add_product_to_custom_category():
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
    custom_category = CustomCategory(**{"name": "atish bazi"})
    custom_category.add_product(product.dict())
    yield custom_category
    product.delete()


@pytest.fixture
def add_and_remove_product_from_category():
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
    custom_category = CustomCategory(**{"name": "atish bazi"})
    custom_category.add_product(product.dict())
    yield custom_category
    custom_category.remove_product(product.dict())
    product.delete()


@pytest.fixture
def delete_product_from_custom_category():
    yield
    product = Product.construct()
    product = product.get(system_code="100111001002")
    custom_category = CustomCategory(**{"name": "atish bazi"})
    custom_category.remove_product(product.dict())
    product.delete()
