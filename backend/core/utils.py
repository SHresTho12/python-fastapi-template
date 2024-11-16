import re
import os
import jwt
import uuid
import json
import base64
import shutil
import pyseto
import phonenumbers
from pyseto import Key
from itertools import groupby
from typing import List
from datetime import datetime, timedelta
from fastapi.param_functions import Security

from fastapi.security.http import HTTPAuthorizationCredentials, HTTPBearer

from auth import User

from fastapi import status, HTTPException, UploadFile

from core import enums
from core.config import API_STR
from core.const import METHOD_TYPE

from config import get_settings, logger

security = HTTPBearer()

ALLOWED_FILE_EXTENSIONS = ['jpg', 'jpeg', 'png']


def encoding_base64_string(value: str) -> str:
    value_bytes = value.encode('ascii')
    base64_bytes = base64.b64encode(value_bytes)
    base64_value = base64_bytes.decode('ascii')
    return base64_value


def decoding_base64_string(base64_value: str) -> str:
    base64_bytes = base64_value.encode('ascii')
    message_bytes = base64.b64decode(base64_bytes)
    value = message_bytes.decode('ascii')
    return value


def file_upload(file: UploadFile, upload_path: str) -> str:
    real_file_size = 0
    # for chunk in file.file:
    #     real_file_size += len(chunk)
    #     if real_file_size > 500000:
    #         raise HTTPException(
    #             status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
    #             detail="Image size is too large. Please upload image less than 500 kb"
    #         )
    filename = file.filename
    split_file_name = os.path.splitext(filename)
    file_extension = split_file_name[1].split('.')[-1]
    if file_extension.lower() not in ALLOWED_FILE_EXTENSIONS:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"Image type must be one of {', '.join(ALLOWED_FILE_EXTENSIONS)}"
        )
    if not os.path.exists(upload_path):
        os.makedirs(upload_path)
    new_name = f"{str(uuid.uuid4().hex)}.{file_extension}"
    file_location = f"{upload_path}/{new_name}"
    with open(file_location, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    return file_location


def number_format(number, decimal_point=5):
    if (decimal_point == None):
        return number
    else:
        return round(number, decimal_point)


def remove_special_sentence(sentence, character):
    return ''.join(character if a == character else ''.join(b) for a, b in groupby(sentence))


def get_all_api_endpoint(request):
    api_end_point_set = set()
    url_method_dict = {}
    for route in request.app.routes:
        if re.search(f"{API_STR}/", str(route.path)):
            tags = str(route.tags[0]).lower()
            if not tags == "public" and not tags == "auth":
                _path = route.path
                for key in route.param_convertors.keys():
                    key = "/{" + key + "}"
                    _path = _path.replace(key, "")
                _path = remove_special_sentence(_path, "/")
                _path = _path.replace(f"{API_STR}/", "")
                _path = _path.replace("/", "_")
                api_end_point_set.add(_path)
                if not _path in url_method_dict:
                    url_method_dict[_path] = []
                methods = list(route.__dict__.get('methods'))

                method_type = METHOD_TYPE[methods[0].lower()]
                if method_type == 'view' and not route.param_convertors:
                    method_type = 'list'
                url_method_dict[_path].append(method_type)

    return api_end_point_set, url_method_dict

async def get_public_api_end_point(request):
    print(">>>>>>>>>>>>>>>>>>>>>>>>>>>>>")
    api_end_point_set, url_method_dict = get_all_api_endpoint(request)
    return list(api_end_point_set)



async def phone_number_validation_check(user) -> str:
    if user.phone:
        user.phone = str(''.join([n for n in user.phone if n.isdigit() or n == '+']))
        print(user.phone)
        try:
            phone = phonenumbers.parse(user.phone)
            if phonenumbers.is_valid_number(phone):
                return user.phone
            raise
        except:
            raise HTTPException(
                status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="Invalid phone number, please, provide a valid phone number based on the country you have selected!",
            )
    else:
        return None


def encoding_token(token_data: dict) -> str:
    expire = datetime.utcnow() + timedelta(minutes=get_settings().access_token_expire_minutes)
    token_data.update({"exp": expire, 'token_type': 'access'})
    encoded_jwt = jwt.encode(token_data, get_settings().jwt_secret_key, algorithm=get_settings().jwt_algorithm)
    print("token: ", encoding_base64_string(str(encoded_jwt)))
    return encoding_base64_string(str(encoded_jwt))


def decoding_token(token: str) -> int:
    try:
        payload = jwt.decode(
            str(decoding_base64_string(token)),
            get_settings().jwt_secret_key,
            algorithms=[get_settings().jwt_algorithm]
        )
        return payload
    except:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Invalid or expired token!"
        )


async def request_user(
        auth_info: HTTPAuthorizationCredentials = Security(security),
) -> User:
    try:
        local_key = Key.new(version=4, purpose="local", key=get_settings().paseto_local_key)
        decoded = pyseto.decode(local_key, auth_info.credentials)
        payload = decoded.payload.decode()
        print(payload)
        payload = json.loads(payload)
    except:
        raise HTTPException(
            detail="Could not validate credentials.",
            status_code=status.HTTP_401_UNAUTHORIZED,
        )
    if isinstance(payload, dict):
        data = payload.get('data', {})
        id = data.get('id', None)
        email = data.get('email', None)
        if not id or not email:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="Could not validate credentials."
            )
        from auth.repository import AuthRepo
        auth_repo = AuthRepo()
        async with auth_repo:
            user = await auth_repo.get(
                filters=(
                    User.email == email,
                    User.id == id
                )
            )
        if user:
            return user
    raise HTTPException(
        detail="Could not validate credentials.",
        status_code=status.HTTP_401_UNAUTHORIZED,
    )


async def enum_to_dictionary(any_enum, hidden_keys: List = []):
    return {
        key.name.title(): key.value
        for key in any_enum
        if key.name not in hidden_keys
    }


async def get_all_status(request):
    return {
        "status": await enum_to_dictionary(enums.Status),
        "menu_type": await enum_to_dictionary(enums.MenuType),
        "permission_type": await enum_to_dictionary(enums.PermissionType),
        "gender": await enum_to_dictionary(enums.Gender),
        "api_end_point": await get_public_api_end_point(request)
    }

async def get_folder_name(
        kwargs_data,
):
    try:
        project_environment = "dev"
        module = "others"
        file_type = "others"
        if "project_environment" in kwargs_data:
            project_environment = kwargs_data["project_environment"]
        if "module_name" in kwargs_data:
            module = kwargs_data["module_name"]
        if "file_type" in kwargs_data:
            file_type = kwargs_data["file_type"]

        return f"{project_environment}/{module}/{file_type}"
    except Exception as e:
        logger.error(e)
        return None


async def upload_file_to_s3(
        file_obj,
        file_name,
        **kwargs
):
    get_folders = await get_folder_name(kwargs_data=kwargs)
    object_key = f"{get_folders}/{file_name}" if get_folders else file_name

    session = aioboto3.Session(
        region_name=get_config().aws_region,
        aws_access_key_id=get_config().aws_access_key_id,
        aws_secret_access_key=get_config().aws_secret_access_key
    )
    async with session.client('s3') as s3_client:
        try:
            await s3_client.upload_fileobj(
                file_obj,
                get_config().aws_s3_bucket,
                object_key
            )
            logger.debug(
                f"Successfully Uploaded. Object Key: {object_key}"
            )
        except Exception as e:
            logger.error(f"{e}")