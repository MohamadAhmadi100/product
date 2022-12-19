class Basket:
    @staticmethod
    def set_mandatory_products(mandatory_products, products):
        new_mandatory_products = []
        if not len(mandatory_products) or not len(products):
            return None, False
        for product in products:
            if not product.get("quantity"):
                return None, False
            for mandatory_product in mandatory_products:
                if mandatory_product.get("systemCode") == product.get("system_code"):
                    if mandatory_product.get("quantity") > product.get("quantity"):
                        return None, False
                    product["count"] = mandatory_product.get("quantity")
                    product["price"] = mandatory_product.get("basketPrice")
                    product["storage_id"] = mandatory_product.get("storageId")
                    new_mandatory_products.append(product)
        if len(new_mandatory_products) != len(mandatory_products):
            return None, False
        return new_mandatory_products, True

    @staticmethod
    def set_selective_products(selective_products, products, basket_min_quantity):
        new_selective_products = []
        if len(selective_products) < basket_min_quantity or len(products) < basket_min_quantity:
            return None, False
        for product in products:
            if not product.get("quantity"):
                return None, False
            for selective_product in selective_products:
                if not selective_product.get("minQuantity") and not selective_product.get("quantity"):
                    return None, False
                if selective_product.get("systemCode") == product.get("system_code"):
                    min_quantity = selective_product.get("minQuantity") or selective_product.get("quantity")
                    max_quantity = selective_product.get("maxQuantity") or selective_product.get("quantity")
                    if min_quantity > product.get("quantity"):
                        return None, False
                    product["minQuantity"] = min_quantity if min_quantity >= product.get("min_qty") else product.get(
                        "min_qty")
                    product["maxQuantity"] = max_quantity if max_quantity <= product.get("max_qty") else product.get(
                        "max_qty")
                    product["count"] = min_quantity if min_quantity == max_quantity else 0
                    product["price"] = selective_product.get("basketPrice")
                    product["storage_id"] = selective_product.get("storageId")
                    new_selective_products.append(product)
        if len(new_selective_products) < basket_min_quantity:
            return None, False
        return new_selective_products, True

    @staticmethod
    def set_optional_products(optional_products, products):
        new_optional_products = []
        for product in products:
            if not product.get("quantity"):
                continue
            for optional_product in optional_products:
                min_quantity = optional_product.get("minQuantity") or optional_product.get("quantity")
                max_quantity = optional_product.get("maxQuantity") or optional_product.get("quantity")
                if not min_quantity:
                    continue
                if optional_product.get("systemCode") == product.get("system_code"):
                    if min_quantity > product.get("quantity"):
                        continue
                    product["minQuantity"] = min_quantity if min_quantity >= product.get("min_qty") else product.get(
                        "min_qty")
                    product["maxQuantity"] = max_quantity if max_quantity <= product.get("max_qty") else product.get(
                        "max_qty")
                    product["count"] = min_quantity if min_quantity == max_quantity else 0
                    product["price"] = optional_product.get("basketPrice")
                    product["storage_id"] = optional_product.get("storageId")
                    new_optional_products.append(product)
        return new_optional_products
