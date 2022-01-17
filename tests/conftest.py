import pytest

from app.models.custom_category import CustomCategory
from app.models.product import Product


@pytest.fixture
def create_and_delete_product():
    sample_data = {
        "system_code": "100104021006",
        "attributes": {
            "image": "/src/default.jpg",
            "year": 2020
        }
    }
    product = Product(**sample_data)
    product.create()
    yield product
    product.get('100104021006')
    product.delete()


@pytest.fixture
def create_product():
    sample_data = {
        "system_code": "100104021006",
        "attributes": {
            "image": "/src/default.jpg",
            "year": 2020
        }
    }
    product = Product(**sample_data)
    product.create()
    yield product


@pytest.fixture()
def create_and_delete_multiple_products():
    system_code_list = ['100201002002', '100101047003', '100104021006']
    for item in system_code_list:
        product = Product(**{
            "system_code": item,
            "attributes": {
                "image": "/src/default.jpg",
                "year": 2020
            }
        })
        product.create()
    yield
    product = Product.construct()
    for system_code in system_code_list:
        product.get(system_code)
        product.delete()


@pytest.fixture
def delete_product():
    yield
    product = Product.construct()
    product.get("100104021006")
    product.delete()


@pytest.fixture
def add_product_to_custom_category():
    sample_data = {
        "system_code": "100104021006",
        "attributes": {
            "image": "/src/default.jpg",
            "year": 2020
        }
    }
    product = Product(**sample_data)
    product.create()
    custom_category = CustomCategory(**{"name": "atish bazi"})
    custom_category.add(product.dict())
    yield custom_category
    product = Product.construct()
    product.get("100104021006")
    product.delete()


@pytest.fixture
def add_and_remove_product_from_category():
    sample_data = {
        "system_code": "100104021006",
        "attributes": {
            "image": "/src/default.jpg",
            "year": 2020
        }
    }
    product = Product(**sample_data)
    product.create()
    custom_category = CustomCategory(**{"name": "atish bazi"})
    custom_category.add(product.dict())
    yield
    custom_category.remove(product.dict())
    product.delete()


@pytest.fixture
def delete_product_from_custom_category():
    yield
    sample_data = {
        "system_code": "100104021006",
        "attributes": {
            "image": "/src/default.jpg",
            "year": 2020
        }
    }
    product = Product(**sample_data)
    product.create()
    product = product.get("100104021006")
    custom_category = CustomCategory(**{"name": "atish bazi"})
    custom_category.remove(product.dict())
    product = Product.construct()
    product.get("100104021006")
    product.delete()
