from typing import Dict

from fastapi import Query, Path, HTTPException, APIRouter, Body

from app.models.product import CreateParent, CreateChild, AddAtributes, Product
from app.modules.attribute_setter import attribute_setter
from app.modules.kowsar_getter import KowsarGetter

router = APIRouter()


@router.get("/product/parent/{system_code}/configs/", status_code=200)
def get_parent_config(system_code: str):
    return CreateParent.get_configs(system_code)


@router.get("/product/parent/", status_code=200)
def create_parent_schema():
    return CreateParent.schema().get("properties")


@router.post("/product/parent/", status_code=201)
def create_parent(
        item: CreateParent
) -> dict:
    """
    Create a product for sale in main collection in database.
    attributes will be validated before insert.
    """
    if item.system_code_is_unique():
        message, success = item.create()
        if success:
            return message
        raise HTTPException(status_code=417, detail=message)
    raise HTTPException(status_code=409, detail={"message": "product already exists", "label": "محصول موجود است",
                                                 "redirect": "/product/{system_code}"})


@router.get("/product/{system_code}/items", status_code=200)
def suggest_product(system_code: str = Path(..., min_length=11, max_length=11)):
    data = KowsarGetter.system_code_items_getter(system_code[:9])
    parents_data = KowsarGetter.get_parents(system_code)
    if parents_data:
        config = (parents_data.get("attributes").get("storage"), parents_data.get("attributes").get("ram"))
        suggests = CreateChild.suggester(data, system_code, config)
        return suggests
    raise HTTPException(status_code=404,
                        detail={"message": "product couldn't found", "label": "محصول یافت نشد",
                                "redirect": "/product/{system_code}"})


@router.get("/product/child/", status_code=200)
def create_child_schema():
    return CreateChild.schema().get("properties")


@router.post("/product/child/", status_code=201)
def create_child(
        item: CreateChild
) -> dict:
    """
    Create a product for sale in main collection in database.
    attributes will be validated before insert.
    """
    if item.system_code_is_unique():
        message, success = item.create()
        if success:
            return message
        raise HTTPException(status_code=417, detail=message)
    raise HTTPException(status_code=409,
                        detail={"message": "product already exists", "label": "محصول موجود است",
                                "redirect": "/product/{system_code}"})


@router.get("/product/attributes/", status_code=200)
def add_attributes_schema():
    form = Product.schema().get("properties").copy()
    form["system_code"]["minLength"] = 12
    del form["name"]
    return form


@router.post("/product/attributes/", status_code=201)
def add_attributes(
        item: AddAtributes = Body(..., example={
            "system_code": "100104021006",
            "attributes": {
                "image": "/src/default.jpg",
                "year": 2020
            }
        })
) -> dict:
    """
    Create a product for sale in main collection in database.
    attributes will be validated before insert.
    """
    if not item.system_code_is_unique():
        item.validate_attributes()
        message, success = item.create()
        if success:
            return message
        raise HTTPException(status_code=417, detail=message)
    raise HTTPException(status_code=404,
                        detail={"message": "product doesn't exists", "label": "محصول موجود نیست",
                                "redirect": "/product/{system_code}"})


@router.get("/product/{system_code}/{lang}", status_code=200)
def get_product_by_system_code(
        system_code: str = Path(..., min_length=11, max_length=11),
        lang: str = Path("fa_ir", min_length=2, max_length=127)
) -> dict:
    """
    Get a product by system_code in main collection in database.
    """
    result = Product.get_product_by_system_code(system_code, lang)
    if result:
        return result
    raise HTTPException(status_code=404,
                        detail={"message": "product doesn't exists", "label": "محصول موجود نیست",
                                "redirect": "/product/{system_code}"})


@router.delete("/product/{system_code}", status_code=200)
def delete_product(
        system_code: str = Path(..., min_length=3, max_length=255)
) -> dict:
    """
    Delete a product by name in main collection in database.
    """
    product = CreateChild.construct()
    product.system_code = system_code
    if not product.system_code_is_unique():
        message, success = product.delete()
        if success:
            return message
        raise HTTPException(status_code=417, detail=message)
    raise HTTPException(status_code=404, detail={"message": "product not found", "label": "محصول یافت نشد"})


@router.get("/product/update_attribute_collection/", status_code=200)
def update_attribute_collection():
    """
    Update the attribute collection in database.
    """
    # TODO: Later, the attributes below should come from API GW
    attributes = [
        {
            "required": True,
            "use_in_filter": False,
            "use_for_sort": False,
            "default_value": None,
            "values": None,
            "set_to_nodes": False,
            "name": "year",
            "label": "سال",
            "input_type": "Number",
            "parent": "100104021006"
        },
        {
            "required": False,
            "use_in_filter": False,
            "use_for_sort": False,
            "default_value": "/src/default.png",
            "values": None,
            "set_to_nodes": True,
            "name": "image",
            "label": "عکس",
            "input_type": "Media Image",
            "parent": "1001"
        }
    ]
    attribute_setter(attributes)
    return {"message": "attribute collection updated", "label": "جدول تنظیمات بروز شد"}


@router.get("/categories/{system_code}/")
def get_all_categories(system_code: str = Path(00, min_length=2, max_length=6),
                       page: int = Query(1, ge=1, le=1000),
                       per_page: int = Query(15, ge=1, le=1000)):
    """
    """
    return Product.get_all_categories(system_code, page, per_page)


@router.get("/product/mock/")
def get_mock():
    return {
        "system_code": "10010200101",
        "name": "ggg",
        "main_category": "Device",
        "sub_category": "Mobile",
        "brand": "Mobile Apple",
        "model": "iPhone 11",
        "routes": {
            "route": "Device",
            "label": "لوازم الکترونیک ",
            "child": {
                "route": "Mobile",
                "label": "موبایل",
                "child": {
                    "route": "Mobile Apple",
                    "label": "موبایل اپل ",
                }
            }
        },
        "related_products": [{
            "system_code": "10010200101",
            "name": "ggg",
            "colors": [{
                "value": "black",
                "type": "color"}, {
                "value": "black",
                "type": "color"}],
            "price": {
                "regular": 60000000,
                "special": 50000000,
            }}],
        "attributes": {
            "images": {
                "attribute_label": "حافظه داخلی",
                "main_image": "url",
                "closeup_image": "url",
                "other_images": ["url", "url"]
            },
            "storage": {"attribute_label": "حافظه داخلی",
                        "label": "۶۴"},
            "ram": {"attribute_label": "رم",
                    "label": "۸"}
        },
        "visible_to_site": True,
        "products": [
            {
                "system_code": "100102001001",
                "config": {
                    "color": {"attribute_label": "رنگ",
                              "value": "black",
                              "label": "مشکی",
                              "type": "color"},
                    "guarantee": {"attribute_label": "گارانتی",
                                  "value": "awat",
                                  "label": "آوات",
                                  "type": "radio"},
                    "seller": {"attribute_label": "فروشنده",
                               "value": "aasood",
                               "label": "آسود",
                               "type": "radio"},
                    "warehouse": [{"quantity": 21,
                                   "price": 20,
                                   "special_price": None,
                                   "warehouse_id": 1,
                                   "warehouse_state": "aasood",
                                   "warehouse_city": "dev",
                                   "warehouse_state_id": "1",
                                   "warehouse_city_id": "1",
                                   "warehouse_label": "تهران",
                                   "attribute_label": "انبار"},
                                  {"quantity": 22,
                                   "price": 22,
                                   "special_price": 21,
                                   "warehouse_id": 2,
                                   "warehouse_state": "awat",
                                   "warehouse_city": "dev",
                                   "warehouse_state_id": "2",
                                   "warehouse_city_id": "2",
                                   "warehouse_label": "مشهد",
                                   "attribute_label": "انبار"}]
                },
                "visible_to_site": True,
            },
            {
                "system_code": "100102001002",
                "config": {
                    "color": {"attribute_label": "رنگ",
                              "value": "red",
                              "label": "قرمز",
                              "type": "color"},
                    "guarantee": {"attribute_label": "گارانتی",
                                  "value": "awat",
                                  "label": "آوات",
                                  "type": "radio"},
                    "seller": {"attribute_label": "فروشنده",
                               "value": "aasood",
                               "label": "آسود",
                               "type": "radio"},
                    "warehouse": [{"quantity": 21,
                                   "price": 23,
                                   "special_price": None,
                                   "warehouse_id": 1,
                                   "warehouse_state": "aasood",
                                   "warehouse_city": "dev",
                                   "warehouse_state_id": "1",
                                   "warehouse_city_id": "1",
                                   "warehouse_label": "تهران",
                                   "attribute_label": "انبار"},
                                  {"quantity": 12,
                                   "price": 25,
                                   "special_price": 24,
                                   "warehouse_id": 2,
                                   "warehouse_state": "awat",
                                   "warehouse_city": "dev",
                                   "warehouse_state_id": "2",
                                   "warehouse_city_id": "2",
                                   "warehouse_label": "مشهد",
                                   "attribute_label": "انبار"}]
                },
                "visible_to_site": True,
            },
            {
                "system_code": "100102001002",
                "config": {
                    "color": {"attribute_label": "رنگ",
                              "value": "red",
                              "label": "قرمز",
                              "type": "color"},
                    "guarantee": {"attribute_label": "گارانتی",
                                  "value": "awat",
                                  "label": "شرکتی",
                                  "type": "radio"},
                    "seller": {"attribute_label": "فروشنده",
                               "value": "aasood",
                               "label": "آسود",
                               "type": "radio"},
                    "warehouse": [{"quantity": 21,
                                   "price": 26,
                                   "special_price": None,
                                   "warehouse_id": 1,
                                   "warehouse_state": "aasood",
                                   "warehouse_city": "dev",
                                   "warehouse_state_id": "1",
                                   "warehouse_city_id": "1",
                                   "warehouse_label": "تهران",
                                   "attribute_label": "انبار"},
                                  {"quantity": 12,
                                   "price": 28,
                                   "special_price": 27,
                                   "warehouse_id": 2,
                                   "warehouse_state": "awat",
                                   "warehouse_city": "dev",
                                   "warehouse_state_id": "2",
                                   "warehouse_city_id": "2",
                                   "warehouse_label": "مشهد",
                                   "attribute_label": "انبار"}]
                },
                "visible_to_site": True,
            },
            {
                "system_code": "100102001001",
                "config": {
                    "color": {"attribute_label": "رنگ",
                              "value": "black",
                              "label": "مشکی",
                              "type": "color"},
                    "guarantee": {"attribute_label": "گارانتی",
                                  "value": "awat",
                                  "label": "نابغه",
                                  "type": "radio"},
                    "seller": {"attribute_label": "فروشنده",
                               "value": "aasood",
                               "label": "نابغه",
                               "type": "radio"},
                    "warehouse": [{"quantity": 21,
                                   "price": 29,
                                   "special_price": None,
                                   "warehouse_id": 1,
                                   "warehouse_state": "aasood",
                                   "warehouse_city": "dev",
                                   "warehouse_state_id": "1",
                                   "warehouse_city_id": "1",
                                   "warehouse_label": "تهران",
                                   "attribute_label": "انبار"},
                                  {"quantity": 22,
                                   "price": 30,
                                   "special_price": 20,
                                   "warehouse_id": 2,
                                   "warehouse_state": "awat",
                                   "warehouse_city": "dev",
                                   "warehouse_state_id": "2",
                                   "warehouse_city_id": "2",
                                   "warehouse_label": "مشهد",
                                   "attribute_label": "انبار"}]
                },
                "visible_to_site": True,
            }
        ]
    }


from pydantic import BaseModel, validator


class Test(BaseModel):
    attributes: dict

    @validator("attributes")
    def attributes(cls, value):
        if not isinstance(value, dict):
            raise HTTPException(detail={"error": "bad attributes"})


class AttributesValidator:
    def __init__(self, attributes):
        self.attributes = attributes
        self.requireds = []
        self.values = []

    def validate(self):
        for item in self.attributes:
            if item.get("required"):
                self.requireds.append(item.get("name"))
            if item.get("values"):
                self.values.append((item.get("name"), item.get("values")))

        self.required_validator()
        self.required_validator()

    def required_validator(self):
        for required in self.requireds:
            if required not in self.attributes.keys():
                raise HTTPException(detail={"error": f"{required} is required"})

    def values_validator(self):
        for value in self.values:
            if value[0] in self.attributes.keys():
                if self.attributes.get(value[0]) not in value[1]:
                    raise HTTPException(detail={"error": f"{value[0]} is not valid"})


attributes_mock = [
    {
        "required": True,
        "use_in_filter": False,
        "use_for_sort": False,
        "default_value": None,
        "values": None,
        "set_to_nodes": False,
        "name": "year",
        "label": "سال",
        "input_type": "Number",
        "parent": "100104021006"
    },
    {
        "required": False,
        "use_in_filter": False,
        "use_for_sort": False,
        "default_value": "/src/default.png",
        "values": None,
        "set_to_nodes": True,
        "name": "image",
        "label": "عکس",
        "input_type": "Media Image",
        "parent": "1001"
    }
]


@router.post("test/bemola")
def testing(item: Test):
    AttributesValidator(item.attributes).validate()
    return item.attributes
