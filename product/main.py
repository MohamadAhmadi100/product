from typing import Optional, Any

from fastapi import FastAPI
from pydantic import BaseModel, validator

from database.models import Product, Assignees
from product.module.attributes import Attributes
from module.kowsar_getter import KowsarGetter
from module.validation_of_attributes import Validates

tags_metadata = [
    {
        "name": "Product",
        "description": "Product related endpoints",
    },
    {
        "name": "Kowsar",
        "description": "Kowsar related endpoints",
    },
    {
        "name": "attribute",
        "description": "attribute crud api",
    }
]
app = FastAPI(
    title="Product API",
    description="This is a simple microservice for product...",
    version="0.1.0",
    openapi_tags=tags_metadata,
)

product = Product()


class Products(BaseModel):
    system_code: str
    specification: dict

    @validator('system_code')
    def system_code_validator(cls, value):
        if type(value) is not str:
            raise ValueError('system_code must be a string')
        elif 2 >= len(value) >= 255:
            raise ValueError('system_code must be between 2 and 255 characters')
        return value


@app.post("/item", tags=["Product"])
def create_product(item: Products):
    spec = Validates.attribute_validation(system_code=item.system_code, attr_names=item.specification)
    system_code = product.create_product(system_code=item.system_code, specification=spec)
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


@app.get("/attribute_by_kowsar/", tags=["attribute"], status_code=200)
def update_product_by_set_to_nodes():
    result = Assignees.set_all_attributes_by_set_to_nodes()
    if result:
        return {'status': 'success'}
    return {'error': 'update attribute failed'}


@app.get("/attribute/", tags=["attribute"], status_code=200)
def get_all_attribute():
    result = Assignees.get_all_attributes_from_attribute_api()
    return {'result': result}


@app.post("/validate/{system_code}/{specification}", status_code=200)
def attribute_validators(item: Products):
    return Validates.attribute_validation(system_code=item.system_code, attr_names=item.specification)


@app.get("/attributes/{system_code}", status_code=200)
def get_all_attribute_by_system_code(system_code: str):
    return Product.get_all_attribute_by_system_code(system_code=system_code)

