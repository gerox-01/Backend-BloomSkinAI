"""
Database session management using SQLAlchemy async.
"""
from typing import AsyncGenerator, Optional

from sqlalchemy.ext.asyncio import AsyncSession, AsyncEngine, create_async_engine, async_sessionmaker
from sqlalchemy.orm import declarative_base

from app.core.config import settings
from app.core.logging import logger

# Global variables for lazy initialization
_engine: Optional[AsyncEngine] = None
_async_session_local: Optional[async_sessionmaker] = None

# Base class for ORM models
Base = declarative_base()


def get_engine() -> AsyncEngine:
    """Get or create the async database engine."""
    global _engine
    if _engine is None:
        if not settings.DATABASE_URL:
            raise ValueError(
                "DATABASE_URL not configured. "
                "Using Firestore? No PostgreSQL database needed. "
                "If you need PostgreSQL, set DATABASE_URL in environment variables."
            )
        logger.info("Creating database engine")
        _engine = create_async_engine(
            settings.DATABASE_URL,
            echo=settings.DEBUG,
            pool_size=settings.DATABASE_POOL_SIZE,
            max_overflow=settings.DATABASE_MAX_OVERFLOW,
            pool_pre_ping=True,
        )
    return _engine


def get_async_session_local() -> async_sessionmaker:
    """Get or create the async session factory."""
    global _async_session_local
    if _async_session_local is None:
        logger.info("Creating async session factory")
        engine = get_engine()
        _async_session_local = async_sessionmaker(
            engine,
            class_=AsyncSession,
            expire_on_commit=False,
            autocommit=False,
            autoflush=False,
        )
    return _async_session_local


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """
    Dependency for getting database session.

    Yields:
        AsyncSession: Database session
    """
    session_local = get_async_session_local()
    async with session_local() as session:
        try:
            yield session
            await session.commit()
        except Exception as e:
            await session.rollback()
            logger.error(f"Database session error: {e}")
            raise
        finally:
            await session.close()


async def init_db() -> None:
    """Initialize database - create all tables."""
    engine = get_engine()
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    logger.info("Database initialized successfully")


async def close_db() -> None:
    """Close database connections."""
    global _engine
    if _engine is not None:
        await _engine.dispose()
        _engine = None
        logger.info("Database connections closed")
