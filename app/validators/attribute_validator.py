def attribute_validator(kowsar_attribute_collection: list, item: dict):
    new_attributes = dict()
    for attribute in kowsar_attribute_collection:
        if attribute.get("label") in item.get("attributes").keys():
            if attribute.get("label") == "Yes or No":
                if not isinstance(item.get("attributes", {}).get(attribute.get("label")), bool):
                    raise HTTPException(status_code=417, detail=f'attribute {attribute.get("label")} must be boolean')
                new_attributes[attribute.get("label")] = item.get("attributes", {}).get(attribute.get("label"))
            elif attribute.get("label") == "Multiple Select":
                if not isinstance(item.get("attributes", {}).get(attribute.get("label")), list):
                    raise HTTPException(status_code=417, detail=f'attribute {attribute.get("label")} must be list')
                elif [value for value in item.get("attributes", {}).get(attribute.get("label")) if
                      value not in attribute.get("values")]:
                    raise HTTPException(status_code=417, detail=f'attribute {attribute.get("label")} is not in values')
                new_attributes[attribute.get("label")] = item.get("attributes", {}).get(attribute.get("label"))
            elif attribute.get("label") == "Price":
                if not isinstance(item.get("attributes", {}).get(attribute.get("label")), int):
                    raise HTTPException(status_code=417, detail=f'attribute {attribute.get("label")} must be integer')
                elif item.get("attributes", {}).get(attribute.get("label")) < 0 or item.get("attributes", {}).get(
                        attribute.get("label")) > 1000000000000:
                    raise HTTPException(status_code=417,
                                        detail=f'attribute {attribute.get("label")} must be between 0 and 1000000000000')
                new_attributes[attribute.get("label")] = item.get("attributes", {}).get(attribute.get("label"))
            elif attribute.get("label") == "Number":
                if not isinstance(item.get("attributes", {}).get(attribute.get("label")), float):
                    raise HTTPException(status_code=417, detail=f'attribute {attribute.get("label")} must be float')
                elif item.get("attributes", {}).get(attribute.get("label")) < 0 or item.get("attributes", {}).get(
                        attribute.get("label")) > 1000000000000:
                    raise HTTPException(status_code=417,
                                        detail=f'attribute {attribute.get("label")} must be between 0 and 1000000000000')
                new_attributes[attribute.get("label")] = item.get("attributes", {}).get(attribute.get("label"))
            elif attribute.get("label") == "Dropdown":
                if item.get("attributes", {}).get(attribute.get("label")) not in attribute.get("values"):
                    raise HTTPException(status_code=417, detail=f'attribute {attribute.get("label")} is not in values')
                new_attributes[attribute.get("label")] = item.get("attributes", {}).get(attribute.get("label"))
            else:
                if not isinstance(item.get("attributes", {}).get(attribute.get("label")), str):
                    raise HTTPException(status_code=417, detail=f'attribute {attribute.get("label")} must be string')
                new_attributes[attribute.get("label")] = item.get("attributes", {}).get(attribute.get("label"))
        elif attribute.get("required"):
            raise HTTPException(status_code=417, detail=f'attribute {attribute.get("label")} is required')
        else:
            new_attributes[attribute.get("label")] = attribute.get("default_value")
    item["attributes"] = new_attributes
    return item
