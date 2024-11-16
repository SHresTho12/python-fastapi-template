from fastapi import FastAPI, Request
from pydantic import ValidationError
from fastapi.responses import JSONResponse

def validation_exception_handler(request: Request, exc: ValidationError):
    errors = exc.errors()
    error_messages = []
    for error in errors:
        loc = error['loc'][1]  # The location of the error
        msg = error['msg']  # The error message
        error_messages.append(f"{loc}: {msg}")  # Custom error message formatting

    return JSONResponse(
        status_code=422,
        content={
            "detail": error_messages,
            "path": request.url.path,
            "method": request.method
        }
    )

