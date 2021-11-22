import sys

sys.path.append("..")

from fastapi import FastAPI

from source.models import Product

app = FastAPI()

product = Product()


@app.post("/item/", status_code=200)
async def create_product(system_code: str):
    system_code = product.create_product(system_code=system_code)
    return {"system_code": system_code}


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
