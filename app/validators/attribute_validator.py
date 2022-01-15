from fastapi import HTTPException


def attribute_validator(kowsar_attribute_collection: list, item):
    new_attributes = dict()
    for attribute in kowsar_attribute_collection:
        kowsar_attribute_name = attribute.get("name")
        kowsar_attribute_type = attribute.get("input_type")
        if kowsar_attribute_name in item.attributes.keys():
            item_attribute_value = item.attributes.get(kowsar_attribute_name)
            if kowsar_attribute_type == "Yes or No":
                if not isinstance(item_attribute_value, bool):
                    raise HTTPException(status_code=417, detail=f'attribute {kowsar_attribute_name} must be boolean')
                new_attributes[kowsar_attribute_name] = item_attribute_value
            elif kowsar_attribute_type == "Multiple Select":
                if not isinstance(item_attribute_value, list):
                    raise HTTPException(status_code=417, detail=f'attribute {kowsar_attribute_name} must be list')
                elif [value for value in item_attribute_value if
                      value not in attribute.get("values")]:
                    raise HTTPException(status_code=417, detail=f'attribute {kowsar_attribute_name} is not in values')
                new_attributes[kowsar_attribute_name] = item_attribute_value
            elif kowsar_attribute_type == "Price":
                if not isinstance(item_attribute_value, int):
                    raise HTTPException(status_code=417, detail=f'attribute {kowsar_attribute_name} must be integer')
                elif item_attribute_value < 0 or item_attribute_value > 1000000000000:
                    raise HTTPException(status_code=417,
                                        detail=f'attribute {kowsar_attribute_name} must be between 0 and 1000000000000')
                new_attributes[kowsar_attribute_name] = item_attribute_value
            elif kowsar_attribute_type == "Number":
                if not isinstance(item_attribute_value, float) and not isinstance(
                        item_attribute_value, int):
                    raise HTTPException(status_code=417,
                                        detail=f'attribute {kowsar_attribute_name} must be float or int')
                elif item_attribute_value < 0 or item_attribute_value > 1000000000000:
                    raise HTTPException(status_code=417,
                                        detail=f'attribute {kowsar_attribute_name} must be between 0 and 1000000000000')
                new_attributes[kowsar_attribute_name] = item_attribute_value
            elif kowsar_attribute_type == "Dropdown":
                if item_attribute_value not in attribute.get("values"):
                    raise HTTPException(status_code=417, detail=f'attribute {kowsar_attribute_name} is not in values')
                new_attributes[kowsar_attribute_name] = item_attribute_value
            else:
                if not isinstance(item_attribute_value, str):
                    raise HTTPException(status_code=417, detail=f'attribute {kowsar_attribute_name} must be string')
                new_attributes[kowsar_attribute_name] = item_attribute_value
        elif attribute.get("required"):
            raise HTTPException(status_code=417, detail=f'attribute {kowsar_attribute_name} is required')
        else:
            new_attributes[kowsar_attribute_name] = attribute.get("default_value")
    item.attributes = new_attributes
    return item
