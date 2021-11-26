from fastapi import FastAPI
from pydantic import BaseModel

from database.models import Product
from module.kowsar_getter import KowsarGetter
from module.attributes import Attributes

app = FastAPI()

product = Product()


# def create_product():
#     attr = [{'category': 'model', 'name': 'image', 'type': 'str', 'is_required': 'True', 'default_value': '/src/default.png', 'values': []},
#             {'category': 'model', 'name': 'price', 'type': 'int', 'is_required': 'True', 'default_value': '0', 'values': []}]
#     command = '@app.post("/item/", status_code=200)\nasync def create_product(system_code: str'
#     for x in attr:
#         if x.get('category') == 'model':
#             command += ',' + x.get('name') + ':' + x.get('type')
#     command += '):\n\tsystem_code = product.create_product(system_code=system_code'
#     for x in attr:
#         command += ',' + x.get('name') + '=' + x.get('name')
#     command += ')\n\treturn {"system_code": system_code}\n'
#     exec(command)
#
#
# create_product()


# @app.post("/item/", status_code=200)
# async def create_product(system_code: str):
#     system_code = product.create_product(system_code=system_code)
#     return {"system_code": system_code}
class Product(BaseModel):
    system_code: str
    specification: dict


@app.post("/item/")
def create_product(item: Product):
    system_code = product.create_product(system_code=item.system_code, specification=item.specification)
    return {"system_code": system_code}


@app.get("/item/get_attr/{system_code}", status_code=200)
def get_attr(system_code: str):
    attributes = Attributes()
    attrs = attributes.get_attributes(system_code)
    return attrs


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
