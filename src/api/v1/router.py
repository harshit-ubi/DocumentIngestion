from fastapi import APIRouter
from src.api.v1.endpoints import health, ingestion, search

api_router = APIRouter()
api_router.include_router(health.router, tags=["Health"])
api_router.include_router(ingestion.router, tags=["Ingestion"])
api_router.include_router(search.router, tags=["Search"])