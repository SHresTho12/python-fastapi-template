from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

def add_middleware(app: FastAPI) -> None:
    # add cors middleware
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
