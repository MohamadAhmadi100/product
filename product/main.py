from fastapi import FastAPI
from pydantic import BaseModel

from database.models import Product
from module.kowsar_getter import KowsarGetter
from module.attributes import Attributes

app = FastAPI()

product = Product()


class Attribute(BaseModel):
    category: str
    name: str
    type: str
    is_required: str
    default_value: str
    values: list
    set_to_nodes: bool


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


@app.post("/item")
def create_product(item: Product):
    system_code = product.create_product(system_code=item.system_code, specification=item.specification)
    return {"system_code": system_code}


@app.get("/kowsar/{system_code}", status_code=200)
def get_kowsar(system_code: str):
    data = KowsarGetter.system_code_name_getter(system_code)
    return data


@app.get("/kowsar/items/{system_code}", status_code=200)
def get_kowsar_items(system_code: str):
    data = KowsarGetter.system_code_items_getter(system_code)
    return data


@app.get("/{page_num}", status_code=200)
def read_products(page_num: int):
    products = product.get_all_products(page=page_num, product_count=3)
    return products


@app.get("/item/{item_id}", status_code=200)
def read_product(item_id: str):
    result = product.get_product(system_code=item_id)
    return result


@app.delete("/item/{item_id}", status_code=204)
def delete_product(item_id: str) -> None:
    product.delete_product(system_code=item_id)
