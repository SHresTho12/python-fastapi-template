import http

from bson.objectid import ObjectId
from fastapi import HTTPException

from constants.auth_consts import SUPER_ADMIN_ROLE


class UserUtils :
    def __init__(self):
        pass

    @staticmethod
    def id_to_object_id(Id: str):
        try:
            return ObjectId(Id)
        except Exception:
            raise HTTPException(
                status_code=http.HTTPStatus.BAD_REQUEST,
                detail="Invalid ID format"
            )
    @staticmethod
    def check_for_super_admin_privilege(token_payload: dict):
        if token_payload['data'].get("role") != SUPER_ADMIN_ROLE:
            raise HTTPException(
                status_code=http.HTTPStatus.FORBIDDEN,
                detail="Only super admin can add new members"
            )