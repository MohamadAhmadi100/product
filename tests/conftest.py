import pytest

from app.models.custom_category import CustomCategory
from app.models.product import Product, CreateParent, CreateChild, AddAtributes
from app.helpers.mongo_connection import MongoConnection


def delete_parent():
    with MongoConnection() as mongo:
        mongo.collection.delete_one({'system_code': '100104021'})


@pytest.fixture
def create_parent():
    sample_data = {
        "system_code": "100104021",
        "name": "ردمی 9c"
    }
    product = CreateParent(**sample_data)
    product.create()
    yield product


@pytest.fixture
def create_and_delete_parent():
    sample_data = {
        "system_code": "100104021",
        "name": "ردمی 9c"
    }
    product = CreateParent(**sample_data)
    product.create()
    yield product
    delete_parent()


@pytest.fixture
def create_child(create_parent):
    sample_data = {
        "system_code": "100104021006"
    }
    product = CreateChild(**sample_data)
    product.create()
    yield product


@pytest.fixture
def add_attributes(create_child):
    AddAtributes(**{
        "system_code": '100104021006',
        "attributes": {
            "image": "/src/default.jpg",
            "year": 2020
        }
    })
    product = AddAtributes.create()
    yield product


@pytest.fixture
def add_product_to_custom_category():
    sample_data = {
        "system_code": "100104021006",
        "attributes": {
            "image": "/src/default.jpg",
            "year": 2020
        }
    }
    product = AddAtributes(**sample_data)
    product.create()
    custom_category = CustomCategory(**{"name": "atish bazi"})
    custom_category.add(product.dict())
    yield custom_category
    product = AddAtributes.construct()
    product.get("100104021")
    delete_parent()


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

