from fastapi import HTTPException


def attribute_validator(kowsar_attribute_collection: list, item):
    new_attributes = dict()
    for attribute in kowsar_attribute_collection:
        if attribute.get("name") in item.attributes.keys():
            if attribute.get("input_type") == "Yes or No":
                if not isinstance(item.attributes.get(attribute.get("name")), bool):
                    raise HTTPException(status_code=417, detail=f'attribute {attribute.get("name")} must be boolean')
                new_attributes[attribute.get("name")] = item.attributes.get(attribute.get("name"))
            elif attribute.get("input_type") == "Multiple Select":
                if not isinstance(item.attributes.get(attribute.get("name")), list):
                    raise HTTPException(status_code=417, detail=f'attribute {attribute.get("name")} must be list')
                elif [value for value in item.attributes.get(attribute.get("name")) if
                      value not in attribute.get("values")]:
                    raise HTTPException(status_code=417, detail=f'attribute {attribute.get("name")} is not in values')
                new_attributes[attribute.get("name")] = item.attributes.get(attribute.get("name"))
            elif attribute.get("input_type") == "Price":
                if not isinstance(item.attributes.get(attribute.get("name")), int):
                    raise HTTPException(status_code=417, detail=f'attribute {attribute.get("name")} must be integer')
                elif item.attributes.get(attribute.get("name")) < 0 or item.attributes.get(
                        attribute.get("name")) > 1000000000000:
                    raise HTTPException(status_code=417,
                                        detail=f'attribute {attribute.get("name")} must be between 0 and 1000000000000')
                new_attributes[attribute.get("name")] = item.attributes.get(attribute.get("name"))
            elif attribute.get("input_type") == "Number":
                if not isinstance(item.attributes.get(attribute.get("name")), float) and not isinstance(item.attributes.get(attribute.get("name")), int):
                    raise HTTPException(status_code=417, detail=f'attribute {attribute.get("name")} must be float')
                elif item.attributes.get(attribute.get("name")) < 0 or item.attributes.get(
                        attribute.get("name")) > 1000000000000:
                    raise HTTPException(status_code=417,
                                        detail=f'attribute {attribute.get("name")} must be between 0 and 1000000000000')
                new_attributes[attribute.get("name")] = item.attributes.get(attribute.get("name"))
            elif attribute.get("input_type") == "Dropdown":
                if item.attributes.get(attribute.get("name")) not in attribute.get("values"):
                    raise HTTPException(status_code=417, detail=f'attribute {attribute.get("name")} is not in values')
                new_attributes[attribute.get("name")] = item.attributes.get(attribute.get("name"))
            else:
                if not isinstance(item.attributes.get(attribute.get("name")), str):
                    raise HTTPException(status_code=417, detail=f'attribute {attribute.get("name")} must be string')
                new_attributes[attribute.get("name")] = item.attributes.get(attribute.get("name"))
        elif attribute.get("required"):
            raise HTTPException(status_code=417, detail=f'attribute {attribute.get("name")} is required')
        else:
            new_attributes[attribute.get("name")] = attribute.get("default_value")
    item.attributes = new_attributes
    return item
