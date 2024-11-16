import os
from config import get_settings

COUNTRY_FILE_UPLOAD_PATH = 'media/country'
PROJECT_INVOICE_FILE_PATH = 'file/project_invoice'
THUMBNAIL_SIZE = (100, 100)

UNIQUE_CODE_DIGIT = 12
GROUP_LIST = {
    1: "Super Admin",
    2: "Admin"

}
GROUP_LIST_REVERSE = dict((v, k) for k, v in GROUP_LIST.items())

MODULE_LIST = {
    1: "Admin Management",
}
METHOD_TYPE = {
    "post": "create",
    "put": "edit",
    "patch": "edit",
    "delete": "delete",
    "get": "view"
}
# Upload Max Size
IMAGE_UPLOAD_MAX_SIZE = 500000  # 500kb
VIDEO_UPLOAD_MAX_SIZE = 4000000  # 4 mb

PAGINATION_PAGE_LIMIT = 10
PAGINATION_PAGE_NUMBER = 1
MAP_URL = lambda route: f"{get_settings().api_str}/{route}"

FREE_CREDIT_BALANCE = 30
DEFAULT_ACTION = {
    "create": True,
    "edit": True,
    "list": True,
    "delete": True,
    "view": True
}


# List filter type enum
class FilterType:
    def __init__(self):
        self.types = {"CONTAINS": "contains", "EXACT": "exact"}

    def __getattr__(self, name):
        return self.types.get(name, None)


FILTERTYPE = FilterType()

