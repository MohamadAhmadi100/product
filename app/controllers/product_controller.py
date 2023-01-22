from app.helpers.basket_calculator import Basket
from app.models.product import Product, AddAttributes, Price, Quantity
from app.modules import csv_getter


def create_product(name, url_name, system_codes):
    """
    Create a product for sale in main collection in database.
    attributes will be validated before insert.
    """
    product = Product(name, url_name, system_codes)
    if product.system_codes_are_unique():
        result = product.make_product_obj()
        if not result:
            return {"success": False, "error": "system codes are not found in kowsar", "status_code": 400}
        success = product.create()
        if success:
            return {"success": True, "message": "products created successfully", "status_code": 201}
        return {"success": False, "error": "products did not created successfully", "status_code": 400}
    return {"success": False, "error": "system codes are not unique", "status_code": 400}


def get_product_attributes(system_code: str) -> dict:
    """
    Get a product by system_code in main collection in database.
    """
    message, result = Product.get_product_attributes(system_code)
    if result:
        return {"success": True, "message": message, "status_code": 200}
    return {"success": False, "error": message, "status_code": 404}


def add_attributes(system_code: str, attributes: dict) -> dict:
    """
    Create a product for sale in main collection in database.
    attributes will be validated before insert.
    """
    attributes = AddAttributes(system_code, attributes)
    if attributes.system_code_exists():
        message, success = attributes.create()
        if success:
            return {"success": True, "message": message, "status_code": 201}
        return {"success": False, "error": message, "status_code": 400}
    return {"success": False, "error": "system code not found", "status_code": 400}


def get_product_backoffice(system_code: str):
    """
    """
    result = Product.get_product_backoffice(system_code)
    if result:
        return {"success": True, "message": result, "status_code": 200}
    return {"success": False, "error": "product not found", "status_code": 404}


def set_product_price(system_code: str, customer_type: dict):
    price = Price(system_code, customer_type)
    if price.system_code_exists():
        result = price.set_product_price()
        if result:
            return {"success": True, "message": "موجودی با موفقیت آپدیت شد", "status_code": 201}
    return {"success": False, "error": "محصول یافت نشد", "status_code": 404}


def update_price(system_code: str, customer_type: str, storage_id: str, regular: int, special: int,
                 informal_price: dict, credit: dict, special_from_date: str, special_to_date: str) -> dict:
    """
    update price (regular & special) by customer type and storage for a system code
    """
    data = Price.update_price(system_code, customer_type, storage_id, regular, special, informal_price, credit,
                              special_from_date, special_to_date)
    if data:
        return {"success": True, "status_code": 202, "message": data}
    return {"success": False, "status_code": 417, "error": "خطا در آپدیت قیمت"}


def get_stock(system_code: str) -> dict:
    """
    get stock of a system_code
    """
    result = Quantity.get_stock(system_code)
    if result['total'] == 0:
        return {"success": False, "status_code": 404, "error": Quantity.get_all_stocks()}
    return {"success": True, "status_code": 200, "message": result}


def set_product_quantity(system_code, customer_types) -> dict:
    """
    set quantity per stock and user type
    """
    quantity = Quantity(system_code, customer_types)
    result = quantity.set_quantity()
    if result:
        return {"success": True, "status_code": 201, "message": "موجودی با موفقیت آپدیت شد"}
    return {"success": False, "status_code": 417, "error": "خطا در آپدیت موجودی!"}


def update_quantity(system_code: str, customer_type: str, storage_id: str, quantity: int,
                    min_qty: int, max_qty: int) -> dict:
    """
    update quantity of a system_code
    """
    result = Quantity.update_quantity(system_code, customer_type, storage_id, quantity, min_qty, max_qty)
    if result:
        return {"success": True, "status_code": 200, "message": result}
    return {"success": False, "status_code": 404, "error": "کالا یافت نشد"}


def get_product_list_back_office(brands: list, warehouses: list, price_from: int, price_to: int, sellers: list,
                                 colors: list, quantity_from: int, quantity_to: int, date_from: str, date_to: str,
                                 guarantees: list, steps: list, visible_in_site: bool, approved: bool, available: bool,
                                 page: int, per_page: int, system_code: str, lang: str) -> dict:
    """
    """
    result = Product.get_product_list_back_office(brands, warehouses, price_from, price_to, sellers, colors,
                                                  quantity_from, quantity_to, date_from, date_to, guarantees, steps,
                                                  visible_in_site, approved, available, page, per_page, system_code,
                                                  lang)
    if result:
        return {"success": True, "message": result, "status_code": 200}
    return {"success": False, "error": "products not found", "status_code": 404}


def edit_product(system_code: str, item: dict) -> dict:
    """
    """
    if Product.system_code_exists(system_code):
        result = Product.edit_product(system_code, item)
        return {"success": True, "message": result, "status_code": 200}

    return {"success": False, "error": {"message": "product not found",
                                        "label": "محصول مورد نظر یافت نشد"}, "status_code": 404}


def get_product_by_system_code(system_code: str, lang: str) -> dict:
    """
    Get a product by system_code in main collection in database.
    """
    result = Product.get_product_by_system_code(system_code, lang)
    if result:
        return {"success": True, "message": result, "status_code": 200}
    return {"success": False, "error": "product not found", "status_code": 404}


def get_products_credit_price_by_system_codes(product_list: dict, lang: str, customer_type) -> dict:
    cart_credit_price = 0
    for product in product_list:
        result = Product.get_product_by_system_code(product.get("system_code"), lang)
        storage_id = product.get("storage_id")
        days = product.get("days")
        pr_storage = result.get("warehouse_details", {}).get(customer_type, {}).get("storages", {}).get(storage_id, {})
        pr_price = pr_storage.get("regular", 0)
        pr_credit = pr_storage.get("credit")
        if pr_credit.get("type") == "fixed":
            cart_credit_price += pr_price + (
                    pr_credit.get("percent", 0) * pr_price
            ) + pr_credit.get("regular", 0)
        elif pr_credit.get("type") == "daily":
            cart_credit_price += pr_price + (
                    pr_credit.get("percent", 0) * pr_price
            ) * days + pr_credit.get("regular", 0) * days
    if cart_credit_price:
        return {"success": True, "message": cart_credit_price, "status_code": 200}
    return {"success": False, "error": "product not found", "status_code": 404}


def get_product_list_by_system_code(system_code, page, per_page, storages, user_allowed_storages, customer_type):
    result = Product.get_product_list_by_system_code(system_code, page, per_page, storages, user_allowed_storages,
                                                     customer_type)
    if result:
        return {"success": True, "message": result, "status_code": 200}
    return {"success": False, "error": "product not found", "status_code": 404}


def get_product_page(system_code: str, user_allowed_storages: list, customer_type: str, lang: str,
                     credit: bool) -> dict:
    """
    Get a product by system_code in main collection in database.
    """
    result = Product.get_product_page(system_code, user_allowed_storages, customer_type, lang, credit)
    if result:
        return {"success": True, "message": result, "status_code": 200}
    return {"success": False, "error": "product not found", "status_code": 404}


def get_product_by_name(name: str, storages: list, user_allowed_storages: list, customer_type: str):
    """
    """
    result = Product.get_product_by_name(name, storages, user_allowed_storages, customer_type)
    if result:
        return {"success": True, "message": result, "status_code": 200}
    return {"success": False, "error": "product not found", "status_code": 404}


def search_product_in_bot(name: str):
    result = Product.search_product_in_bot(name)
    if result:
        return {"success": True, "message": result, "status_code": 200}
    return {"success": False, "error": "product not found", "status_code": 404}


def get_category_list(user_allowed_storages: list, customer_type: str) -> dict:
    """
    Get a product by system_code in main collection in database.
    """
    result = Product.get_category_list(user_allowed_storages, customer_type)
    if result:
        return {"success": True, "message": result, "status_code": 200}
    return {"success": False, "error": "product not found", "status_code": 404}


def search_product_child(name: str, system_code: str, storages: list, customer_type: str,
                         in_stock: bool = False) -> dict:
    """
    Get a product by system_code in main collection in database.
    """
    result = Product.search_product_child(name, system_code, storages, customer_type, in_stock)
    if result:
        return {"success": True, "message": result, "status_code": 200}
    return {"success": False, "error": "product not found", "status_code": 404}


def get_csv(storage_id: str) -> dict:
    """
    Get a product by system_code in main collection in database.
    """
    result = csv_getter.get_csv(storage_id)
    if result:
        return {"success": True, "message": result, "status_code": 200}
    return {"success": False, "error": "product not found", "status_code": 404}


def price_list(customer_type, storage_id, sub_category, brand, model, allowed_storages):
    result = Product.price_list(customer_type, storage_id, sub_category, brand, model, allowed_storages)
    if result:
        return {"success": True, "message": result, "status_code": 200}
    return {"success": False, "error": "product not found", "status_code": 404}


def price_list_all(customer_type, sub_category, brand, model, allowed_storages):
    result = Product.price_list_all(customer_type, sub_category, brand, model, allowed_storages)
    if result:
        return {"success": True, "message": result, "status_code": 200}
    return {"success": False, "error": "product not found", "status_code": 404}


def price_list_tehran(customer_type, sub_category, brand, model, allowed_storages):
    result = Product.price_list_tehran(customer_type, sub_category, brand, model, allowed_storages)
    if result:
        return {"success": True, "message": result, "status_code": 200}
    return {"success": False, "error": "product not found", "status_code": 404}


def get_basket_product(system_code, storage_id, customer_type):
    if result := Product.get_basket_product(system_code, storage_id, customer_type):
        return {"success": True, "message": result, "status_code": 200}
    return {"success": False, "error": "product not found", "status_code": 404}


def get_basket_products(data: list, customer_type: str = "B2B"):
    new_data = []
    for index, basket in enumerate(data):
        product_count = 0
        system_codes = [mandatory_product.get("systemCode") for mandatory_product in basket.get("mandatoryProducts")]
        if products := Product.get_basket_products(system_codes, basket.get("storageId"), customer_type):
            mandatory_result, active = Basket().set_mandatory_products(basket.get("mandatoryProducts"), products,
                                                                       basket.get("storageId"))
            if not active:
                continue
            product_count += len(mandatory_result)
            data[index]["mandatoryProducts"] = mandatory_result
        selective_system_codes = [selective_product.get("systemCode") for selective_product in
                                  basket.get("selectiveProducts")]
        if selective_products := Product.get_basket_products(selective_system_codes, basket.get("storageId"),
                                                             customer_type):
            selective_result, active = Basket().set_selective_products(basket.get("selectiveProducts"),
                                                                       selective_products,
                                                                       basket.get("minSelectiveProductsQuantity"),
                                                                       basket.get("storageId"))
            if not active:
                continue
            product_count += len(selective_result)
            data[index]["selectiveProducts"] = selective_result
        if not basket.get("optionalProducts"):
            if products and selective_products:
                data[index]["productsCount"] = product_count
                new_data.append(data[index])
            continue
        optional_system_codes = [optional_product.get("systemCode") for optional_product in
                                 basket.get("optionalProducts")]
        if optional_products := Product.get_basket_products(optional_system_codes, basket.get("storageId"),
                                                            customer_type):
            optional_result = Basket().set_optional_products(basket.get("optionalProducts"), optional_products,
                                                             basket.get("storageId"))
            data[index]["optionalProducts"] = optional_result
            if products and selective_products:
                product_count += len(optional_result)
                data[index]["productsCount"] = product_count
                new_data.append(data[index])

    return {"success": True, "message": dict({"data": new_data, "totalCount": len(new_data)}),
            "status_code": 200} if len(new_data) else {"success": False, "error": "سبدی برای نمایش وجود ندارد",
                                                       "status_code": 404}


def price_list_bot(customer_type, system_code, initial=False):
    result = Product.price_list_bot(customer_type, system_code, initial)
    if result:
        return {"success": True, "message": result, "status_code": 200}
    return {"success": False, "error": "product not found", "status_code": 404}


def get_items(system_code, customer_type, storage_id):
    result = Product.get_items(system_code, customer_type, storage_id)
    if result:
        return {"success": True, "message": result, "status_code": 200}
    return {"success": False, "error": "product not found", "status_code": 404}


def get_data_price_list_pic(system_code, customer_type, page, per_page, storage_id):
    result = Product.get_data_price_list_pic(system_code, customer_type, page, per_page, storage_id)
    if result:
        return {"success": True, "message": result, "status_code": 200}
    return {"success": False, "error": "product not found", "status_code": 404}


def get_mega_menu(customer_type, user_allowed_storages):
    result = Product.mega_menu(customer_type, user_allowed_storages)
    if result:
        return {"success": True, "message": result, "status_code": 200}
    return {"success": False, "error": "product not found", "status_code": 404}


def get_main_menu(customer_type, user_allowed_storages):
    result = Product.main_menu(customer_type, user_allowed_storages)
    if result:
        result.update({"banners": Product.get_main_manu_banners()})
        return {"success": True, "message": result, "status_code": 200}
    return {"success": False, "error": "product not found", "status_code": 404}


def set_main_menu_banners(sliders, others):
    result = Product.set_main_menu_banners(sliders, others)
    if result:
        return {"success": True, "status_code": 201, "message": "banners updated successfully"}
    return {"success": False, "status_code": 417, "error": "Error while setting banners"}


def get_main_manu_banners():
    result = Product.get_main_manu_banners()
    if result:
        return {"success": True, "message": result, "status_code": 200}
    return {"success": False, "error": "banners not found", "status_code": 404}


def get_products_seller(seller_id, page, per_page, from_date, to_date, from_qty, to_qty, from_price, to_price, search):
    result = Product.get_products_seller(seller_id, page, per_page, from_date, to_date, from_qty, to_qty, from_price,
                                         to_price, search)
    if result:
        return {"success": True, "message": result, "status_code": 200}
    return {"success": False, "error": "product not found", "status_code": 404}


def add_credit_by_category(system_code: str, customer_type: str, credit: dict):
    result = Product.add_credit_by_category(system_code, customer_type, credit)
    if result:
        return {"success": True, "message": "price updated successfully", "status_code": 201}
    return {"success": False, "error": "product not found", "status_code": 404}


def get_torob_data(page, system_code, page_url):
    result = Product.torob(page, system_code, page_url)
    if result:
        return {"success": True, "message": result, "status_code": 200}
    return {"success": False, "error": "product not found", "status_code": 404}
