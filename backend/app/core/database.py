"""
Database setup and engine configuration.
Uses SQLAlchemy with PostgreSQL for robust data persistence.
Includes connection pooling and automatic session management.
"""

from sqlalchemy import create_engine, event, text
from sqlalchemy.orm import sessionmaker, Session, declarative_base
from sqlalchemy.pool import QueuePool
from app.core.config import settings
import logging

logger = logging.getLogger(__name__)

# SQLAlchemy Base for all models
Base = declarative_base()

# Create database engine with connection pooling
engine = create_engine(
    settings.database_url,
    poolclass=QueuePool,
    pool_size=10,
    max_overflow=20,
    echo=settings.database_echo,
    future=True,
)

# SessionLocal factory
SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine,
    expire_on_commit=False,
)


def get_db() -> Session:
    """
    Dependency injection for database sessions.
    Automatically closes session after request.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db():
    """
    Initialize database tables.
    Creates all tables defined in Base.metadata.
    """
    try:
        Base.metadata.create_all(bind=engine)
        logger.info("✅ Database tables initialized successfully")
    except Exception as e:
        logger.error(f"❌ Error initializing database: {e}")
        raise


def drop_all_tables():
    """
    Drop all tables. Use only for development/testing.
    """
    Base.metadata.drop_all(bind=engine)
    logger.warning("⚠️ All database tables dropped")


# Event listener to enable vector extension on PostgreSQL connection
@event.listens_for(engine, "connect")
def receive_connect(dbapi_conn, connection_record):
    """Enable pgvector extension for vector similarity search."""
    try:
        dbapi_conn.execute(text("CREATE EXTENSION IF NOT EXISTS vector"))
    except Exception as e:
        # Extension might already exist or not available
        logger.debug(f"Could not create vector extension: {e}")


# Health check function
def health_check() -> bool:
    """Check database connectivity."""
    try:
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        return True
    except Exception as e:
        logger.error(f"Database health check failed: {e}")
        return False
