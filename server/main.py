import uvicorn
from fastapi import FastAPI

# from starlette.middleware.cors import CORSMiddleware
from core.config import get_config

from api.v1.routers.api_router import api_router
from core.middleware.middleware import add_middleware

config = get_config()

def get_application() -> FastAPI:
    application = FastAPI(
        # title=config.app_name,
        # description=config.app_description,
        # version=config.app_version,
        openapi_url="/api",
        docs_url="/api/docs",
    )
    add_middleware(application)
    return application


app = get_application()


@app.get("/health")
def root():
    return {"message": "Hello, I am still live!"}

# Include the main API router
app.include_router(api_router)


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000, log_level="debug")
