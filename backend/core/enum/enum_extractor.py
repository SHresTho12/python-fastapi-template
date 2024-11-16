from typing import Any

from fastapi import HTTPException, status

from core.enum.enum_json import PROJECT_ENUM


def enum_extractor(enum_name: str, item_id: int, key: str) -> Any:
    item_list = PROJECT_ENUM[f'{enum_name}']

    for item in item_list:
        if item['id'] == item_id:
            return item[f'{key}']
    return None


def enum_to_item_list_by_key(enum_name, key):
    item_list = PROJECT_ENUM[f'{enum_name}']

    return [item[f'{key}'] for item in item_list]


def enum_extractor_by_item(enum_name, search_key, search_value, retrieve_key):
    item_list = PROJECT_ENUM[f'{enum_name}']
    for item in item_list:
        if item.get(search_key) == search_value:
            return item.get(retrieve_key)
    return None


def enum_value_present(enum_name: str, key: str, value: Any) -> bool:
    item_list = PROJECT_ENUM[f'{enum_name}']
    if len(item_list) == 0:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, detail=f"Enum {enum_name} item list is empty")
    if key not in item_list[0]:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, detail=f"Key {key} not found in enum {enum_name}")
    items = [item[f"{key}"] for item in item_list]

    if value in items:
        return True
    return False
