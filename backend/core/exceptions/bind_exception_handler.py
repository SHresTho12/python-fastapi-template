
from pydantic import ValidationError
from fastapi.exceptions import RequestValidationError
from core.exceptions.exception_handler import validation_error_handler


def bind_exception_handler(application):
    application.add_exception_handler(ValidationError, validation_error_handler)
    application.add_exception_handler(RequestValidationError, validation_error_handler)
