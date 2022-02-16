import pytest

from app.helpers.mongo_connection import MongoConnection
from app.controllers.product_controller import *


@pytest.fixture
def create_parent_fixture():
    with MongoConnection() as mongo:
        mongo.collection.delete_one({'system_code': '10011000101'})
        yield
        mongo.collection.delete_one({'system_code': '10011000101'})


@pytest.fixture
def create_child_fixture():
    with MongoConnection() as mongo:
        create_parent('10011000101', name="محصول تست", visible_in_site=True)
        yield
        mongo.collection.delete_one({'system_code': '10011000101'})


@pytest.fixture
def add_attributes_fixture():
    create_parent('10011000101', name="محصول تست", visible_in_site=True)
    create_child("100110001001", "10011000101", True)
    yield
    with MongoConnection() as mongo:
        mongo.collection.delete_one({'system_code': '10011000101'})


@pytest.fixture
def get_product_by_system_code_fixture():
    create_parent('10011000101', name="محصول تست", visible_in_site=True)
    create_child("100110001001", "10011000101", True)
    add_attributes("100110001001", {
        "image": "/src/default.jpg",
        "year": 2020
    })
    yield
    with MongoConnection() as mongo:
        mongo.collection.delete_one({'system_code': '10011000101'})


@pytest.fixture
def delete_product_fixure():
    create_parent('10011000101', name="محصول تست", visible_in_site=True)
    create_child("100110001001", "10011000101", True)
    yield
    with MongoConnection() as mongo:
        mongo.collection.delete_one({'system_code': '10011000101'})
