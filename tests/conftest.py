import pytest

from app.models.attribute import Attribute
from app.models.assignee import Assignee


@pytest.fixture
def create_and_delete_attribute():
    sample_data = {
        "name": "price",
        "label": "قیمت",
        "input_type": 8,
        "required": False,
        "use_in_filter": True,
        "use_for_sort": True,
        "parent": "1001",
        "default_value": 0,
        "values": None,
        "set_to_nodes": True,
    }
    attribute = Attribute(**sample_data)
    attribute.create()
    yield attribute
    attribute.delete()


@pytest.fixture
def create_attribute():
    sample_data = {
        "name": "price",
        "label": "قیمت",
        "input_type": 8,
        "required": False,
        "use_in_filter": True,
        "use_for_sort": True,
        "parent": "1001",
        "default_value": 0,
        "values": None,
        "set_to_nodes": True,
    }
    attribute = Attribute(**sample_data)
    attribute.create()
    yield attribute


@pytest.fixture
def delete_attribute():
    yield
    attribute = Attribute.construct()
    attribute.get("price")
    attribute.delete()


@pytest.fixture
def create_and_delete_multiple_attributes():
    attribute_list = ["test_1", "test_2", "test_3"]
    for item in attribute_list:
        attribute = Attribute(**{
            "name": item,
            "label": "قیمت",
            "input_type": 8,
            "required": False,
            "use_in_filter": True,
            "use_for_sort": True,
            "parent": "1001",
            "default_value": 0,
            "values": None,
            "set_to_nodes": True,
        })
        attribute.create()
    yield
    for item in attribute_list:
        attr = Attribute.construct()
        attr.get(item)
        attr.delete()


@pytest.fixture
def create_and_delete_assignee():
    sample_data = {
        "name": "price",
        "label": "قیمت",
        "input_type": 8,
        "required": False,
        "use_in_filter": True,
        "use_for_sort": True,
        "parent": "1001",
        "default_value": 0,
        "values": None,
        "set_to_nodes": True,
    }
    attribute = Attribute(**sample_data)
    attribute.create()
    sample_assignee = {
        "name": "product"
    }
    assignee = Assignee(sample_assignee.get("name"))
    assignee.add_attribute(attribute)
    yield
    attribute.delete()

