from fastapi import FastAPI
from app.api import api_router

app = FastAPI(
  title="Upload API",
  docs_url="/",
)

app.include_router(api_router, prefix="/api")
