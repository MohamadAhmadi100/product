import pytest

from app.models.product import Product
from app.models.custom_category import CustomCategory


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
    data = {
        "name": "atish bazi"
    }
    category = CustomCategory(**data)
    category.add_product_to_custom_category({
        "system_code": "100101017002",
        "attributes": {
            "image": "/src/default.jpg",
            "year": "2020"
        }
    })
    yield category


@pytest.fixture
def add_and_remove_product_from_category():
    data = {
        "name": "atish bazi"
    }
    category = CustomCategory(**data)
    category.add_product_to_custom_category({
        "system_code": "100101017002",
        "attributes": {
            "image": "/src/default.jpg",
            "year": "2020"
        }
    })
    yield category
    category.remove_product_from_custom_category({
        "system_code": "100101017002",
        "attributes": {
            "image": "/src/default.jpg",
            "year": "2020"
        }
    })

@pytest.fixture
def delete_product_from_custom_category():
    yield
    category = CustomCategory.construct()
    category.