import uvicorn
from fastapi import FastAPI, Request
from fastapi_pagination import add_pagination
from fastapi_pagination.utils import disable_installed_extensions_check
from pydantic import ValidationError
from fastapi.exceptions import RequestValidationError



from api.v1 import routers
from api.v1.routers.api import api_router
from config import get_settings
from core.const import MAP_URL
from core.exceptions.bind_exception_handler import bind_exception_handler
from core.exceptions.exceptions import validation_exception_handler
from core.initialize_data import initialize_data
from core.middleware.middleware import add_middleware

def get_app()->FastAPI:
    application = FastAPI(
        title=str(get_settings().project_title),
        docs_url="/api/docs",
        openapi_url="/api",
        on_startup=[initialize_data.start_initialize_data]
    )
    bind_exception_handler(application)
    add_middleware(app=application)
    add_pagination(application)
    disable_installed_extensions_check()
    application.include_router(api_router)

    return application



app = get_app()


"""Health and Test API start"""
@app.get("/health_check")
def read_root(request: Request):
    return {"data": "success"}


if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        reload=get_settings().is_reload,
        port=get_settings().backend_port,
        access_log=True,
        log_level="debug",
    )
