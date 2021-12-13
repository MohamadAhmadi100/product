from typing import Optional, Any

from fastapi import FastAPI
from pydantic import BaseModel, validator

from database.models import Product
from module.kowsar_getter import KowsarGetter
from module.attributes import Attributes

tags_metadata = [
    {
        "name": "Product",
        "description": "Product related endpoints",
    },
    {
        "name": "Kowsar",
        "description": "Kowsar related endpoints",
    }
]
app = FastAPI(
    title="Product API",
    description="This is a simple microservice for product...",
    version="0.1.0",
    openapi_tags=tags_metadata,
)

product = Product()


class Attribute(BaseModel):
    name: str
    label: str
    input_type: int
    required: bool = False
    use_in_filter: bool = False
    use_for_sort: bool = False
    parent: str
    default_value: Optional[Any] = None
    values: Optional[list] = None
    set_to_nodes: bool = False
    assignee: list

    @validator('default_value')
    def default_value_validator(cls, value):
        if not value:
            if isinstance(value, int) or isinstance(value, float):
                if len(str(value)) > 20:
                    raise ValueError('number values must be under 20 character')
            elif isinstance(value, bool):
                return value
            elif 3 >= len(value) >= 256:
                raise ValueError('default value must be between 3 and 256 characters')

    @validator('name')
    def name_validator(cls, value):
        if type(value) is not str:
            raise ValueError('name must be a string')
        elif 3 >= len(value) >= 255:
            raise ValueError('name must be between 3 and 255 characters')
        return value

    @validator('label')
    def label_validator(cls, value):
        if type(value) is not str:
            raise ValueError('label must be a string')
        elif 3 >= len(value) >= 255:
            raise ValueError('label must be between 3 and 255 characters')
        return value

    @validator('input_type')
    def input_type_validator(cls, value):
        valid_input_types = ['Text Field', 'Text Area', 'Text Editor', 'Date', 'Date and Time', 'Yes or No',
                             'Multiple Select', 'Dropdown', 'Price', 'Media Image', 'Color', 'Number']
        if -1 >= value >= len(valid_input_types):
            raise ValueError(f'input_type should be between 0 and {len(valid_input_types) - 1}')
        elif type(value) is not int:
            raise ValueError('input_type must be an integer')
        return value

    @validator('required')
    def required_validator(cls, value):
        if type(value) is not bool:
            raise ValueError('required must be a bool')
        return value

    @validator('use_in_filter')
    def use_in_filter_validator(cls, value):
        if type(value) is not bool:
            raise ValueError('use_in_filter must be a bool')
        return value

    @validator('use_for_sort')
    def use_for_sort_validator(cls, value):
        if type(value) is not bool:
            raise ValueError('use_for_sort must be a bool')
        return value

    @validator('parent')
    def parent_validator(cls, value):
        if type(value) is not str:
            raise ValueError('parent must be a string')
        elif 3 >= len(value) >= 256:
            raise ValueError('parent must be between 3 and 255 characters')
        return value

    @validator('values')
    def values_validator(cls, value):
        if value is None:
            return value
        if type(value) is not list:
            raise ValueError('values must be a list')
        elif len(value) > 127:
            raise ValueError('values must be between 0 and 128 items')
        for item in value:
            if isinstance(item, int) or isinstance(item, float):
                if len(str(item)) > 20:
                    raise ValueError('number values must be under 20 character')
            elif isinstance(item, bool):
                return value
            elif 3 >= len(item) >= 256:
                raise ValueError('values must be between 3 and 256 characters')
        return value

    @validator('set_to_nodes')
    def set_to_nodes_validator(cls, value):
        if type(value) is not bool:
            raise ValueError('set_to_nodes must be a bool')
        return value

    @validator('assignee')
    def assignee_validator(cls, value):
        if value is None:
            return value
        if type(value) is not list:
            raise ValueError('assignee must be a list')
        elif len(value) > 127:
            raise ValueError('assignee must be between 0 and 128 items')
        for item in value:
            if type(item) is not str:
                raise ValueError('assignee must be a list of strings')
            elif len(item) > 255:
                raise ValueError('assignee must be between 0 and 255 characters')
        return value



class UpdateAttribute(BaseModel):
    name: str


class DeleteAttribute(BaseModel):
    name: str
    delete_from_nodes: bool


class Product(BaseModel):
    system_code: str
    specification: dict


@app.post("/kowsar/item")
def set_attr(item: Attribute):
    attributes = Attributes()
    attributes.set_attributes(category=item.category, name=item.name, d_type=item.type, is_required=item.is_required,
                              default_value=item.default_value, values=item.values, set_to_nodes=item.set_to_nodes)
    return {"status": "success"}


@app.put("/kowsar/{system_code}/attr/{attribute_name}", status_code=200)
def update_attr(system_code: str, attribute_name: str, item: UpdateAttribute):
    attributes = Attributes()
    attributes.update_attributes(category=system_code, old_name=attribute_name, new_name=item.name)
    return {"status": "success"}


@app.get("/kowsar/{system_code}/attr", status_code=200)
def get_attrs(system_code: str):
    attributes = Attributes()
    attrs = attributes.get_attributes(system_code)
    return attrs


@app.delete("/kowsar/{system_code}/attr")
def delete_attribute(system_code: str, item: DeleteAttribute):
    attributes = Attributes()
    attributes.delete_attributes(category=system_code, name=item.name, delete_from_nodes=item.delete_from_nodes)
    return {"status": "success"}


@app.post("/item", tags=["Product"])
def create_product(item: Product):
    system_code = product.create_product(system_code=item.system_code, specification=item.specification)
    return {"system_code": system_code}


@app.get("/kowsar/{system_code}", tags=["Kowsar"], status_code=200)
def get_kowsar(system_code: str):
    data = KowsarGetter.system_code_name_getter(system_code)
    return data


@app.get("/kowsar/items/{system_code}", tags=["Kowsar"], status_code=200)
def get_kowsar_items(system_code: str):
    data = KowsarGetter.system_code_items_getter(system_code)
    return data


@app.get("/{page_num}", tags=["Product"], status_code=200)
def read_products(page_num: int):
    products = product.get_all_products(page=page_num, product_count=3)
    return products


@app.get("/item/{item_id}", tags=["Product"], status_code=200)
def read_product(item_id: str):
    result = product.get_product(system_code=item_id)
    return result


@app.delete("/item/{item_id}", tags=["Product"], status_code=204)
def delete_product(item_id: str) -> None:
    product.delete_product(system_code=item_id)
