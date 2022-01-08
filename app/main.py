import logging
from typing import Optional

from fastapi import FastAPI

from app.models.product import Product
from config import settings
import uvicorn
from fastapi import Query

from app.controllers.product_controller import router as product_router
from app.controllers.kowsar_controller import router as kowsar_router

TAGS_META = [
    {
        "name": "product API",
        "description": "Create, Read, Update and Delete products in main collection.",
    },
    {
        "name": "kowsar",
        "description": "Add or remove attribute to a certain collection called kowsar."
    },
    {
        "name": "attribute",
        "description": "Add or remove attribute to a certain collection called attr_kowsar."
    }
]

app = FastAPI(title="Product",
              description="A microservice to create custom product for other microservices!",
              version="0.1.0",
              openapi_tags=TAGS_META,
              docs_url="/api/v1/docs")

app.include_router(product_router)
app.include_router(kowsar_router)


@app.get("/", status_code=200)
def main_page(
        page: Optional[int] = Query(1, ge=1, le=1000)
) -> list:
    """
    Get all the products in main collection in database.
    It shows 10 products per page.
    """
    product = Product.construct()
    return product.get(page=page)


@app.on_event("startup")
async def startup_event() -> None:
    """
    This function will be called when the application starts.
    """
    logging.basicConfig(
        format='%(asctime)s %(levelname)-8s %(message)s',
        filename="app.log",
        level=logging.INFO,
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    logging.info("Application is starting...")


@app.on_event("shutdown")
def shutdown_event() -> None:
    """
    This function will be called when the application stops.
    """
    logging.log("Application is shutting down...")


if __name__ == '__main__':
    uvicorn.run("main:app", host=settings.UVICORN_HOST, port=settings.UVICORN_PORT, reload=True)
