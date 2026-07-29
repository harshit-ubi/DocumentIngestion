from fastapi import APIRouter
from src.infrastructure.database.connection import db_manager

router = APIRouter()


@router.get("/health", summary="Health Check")
async def health_check():
    """Returns the health status of the application API, database, and pgvector extension."""
    db_health = await db_manager.health_check()
    overall_status = "healthy" if db_health.get("database_connected") else "degraded"

    return {
        "status": overall_status,
        "service": "Document Ingestion Platform",
        "components": db_health,
    }
