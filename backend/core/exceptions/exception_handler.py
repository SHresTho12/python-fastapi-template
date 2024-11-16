from __future__ import annotations

import json
import sys
import traceback
from typing import TYPE_CHECKING

from fastapi.encoders import jsonable_encoder

from core.exceptions.api_response import ValidationResponse, AppValidationResponse

if TYPE_CHECKING:
    from fastapi.exceptions import RequestValidationError
    from pydantic import ValidationError
    from starlette.exceptions import HTTPException
    from starlette.requests import Request

    from app.exceptions.app_exceptions import AppExceptionCase

from starlette.responses import JSONResponse
from starlette.status import (
    HTTP_401_UNAUTHORIZED,
    HTTP_422_UNPROCESSABLE_ENTITY,
    HTTP_500_INTERNAL_SERVER_ERROR,
)




def _build_validation_errors(exc, title: str) -> AppValidationResponse:
    errors = [
        ValidationResponse(
            title=title,
            field=error["loc"][1],
            location=error["loc"][0],
            message=error["msg"],
        )
        for error in exc.errors()
    ]
    return AppValidationResponse(errors=errors)


async def validation_error_handler(_: Request, exc: ValidationError) -> JSONResponse:
    return JSONResponse(
        status_code=HTTP_422_UNPROCESSABLE_ENTITY,
        content=jsonable_encoder(_build_validation_errors(exc, exc.__class__.__name__)),
    )

