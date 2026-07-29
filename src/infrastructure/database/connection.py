from typing import AsyncGenerator, Optional
from contextlib import asynccontextmanager
from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from sqlalchemy import text

from src.core.config import settings
from src.core.logging import logger


class DatabaseSessionManager:
    """
    Singleton class for managing asynchronous PostgreSQL database engine and session pools.
    Follows Singleton pattern to guarantee a single pool across the application.
    """
    _instance: Optional["DatabaseSessionManager"] = None

    def __new__(cls) -> "DatabaseSessionManager":
        if cls._instance is None:
            cls._instance = super(DatabaseSessionManager, cls).__new__(cls)
            cls._instance._engine = None
            cls._instance._sessionmaker = None
        return cls._instance

    def init_db(self, database_url: str = settings.DATABASE_URL) -> None:
        """Initializes the async SQLAlchemy engine and session factory."""
        if self._engine is None:
            logger.info("Initializing Async Database Engine connection pool.")
            self._engine = create_async_engine(
                database_url,
                echo=settings.DEBUG,
                pool_pre_ping=True,
                pool_size=10,
                max_overflow=20,
            )
            self._sessionmaker = async_sessionmaker(
                bind=self._engine,
                autoflush=False,
                expire_on_commit=False,
                class_=AsyncSession,
            )

    async def close(self) -> None:
        """Closes the async database engine connection pool."""
        if self._engine is not None:
            logger.info("Closing Async Database Engine connection pool.")
            await self._engine.dispose()
            self._engine = None
            self._sessionmaker = None

    @asynccontextmanager
    async def session(self) -> AsyncGenerator[AsyncSession, None]:
        """Provides an asynchronous database session context manager."""
        if self._sessionmaker is None:
            self.init_db()

        session: AsyncSession = self._sessionmaker()
        try:
            yield session
            await session.commit()
        except Exception as e:
            await session.rollback()
            logger.error(f"Database session rollback due to exception: {str(e)}")
            raise
        finally:
            await session.close()

    async def health_check(self) -> dict:
        """Checks database connectivity and pgvector extension status."""
        try:
            async with self.session() as session:
                result = await session.execute(text("SELECT 1;"))
                db_healthy = result.scalar() == 1

                # Check pgvector extension status
                ext_result = await session.execute(
                    text("SELECT extname FROM pg_extension WHERE extname = 'vector';")
                )
                pgvector_installed = ext_result.scalar() is not None

                return {
                    "database_connected": db_healthy,
                    "pgvector_enabled": pgvector_installed,
                }
        except Exception as e:
            logger.error(f"Database health check failed: {str(e)}")
            return {
                "database_connected": False,
                "pgvector_enabled": False,
                "error": str(e),
            }


# Global Singleton Database Session Manager instance
db_manager = DatabaseSessionManager()
