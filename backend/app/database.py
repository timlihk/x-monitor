from sqlalchemy import create_engine, MetaData
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from app.config import Config
import logging

logger = logging.getLogger(__name__)

def create_database_engine():
    """
    Create database engine with appropriate configuration for SQLite or PostgreSQL.
    """
    db_url = Config.DB_URL
    
    if "sqlite" in db_url.lower():
        # SQLite configuration
        connect_args = {"check_same_thread": False}
        engine_kwargs = {
            "connect_args": connect_args,
            "echo": False  # Set to True for SQL debugging
        }
        logger.info("Configuring SQLite database")
        
    elif "postgresql" in db_url.lower():
        # PostgreSQL configuration
        engine_kwargs = {
            "pool_size": 5,
            "max_overflow": 10,
            "pool_pre_ping": True,  # Verify connections before use
            "pool_recycle": 3600,   # Recycle connections every hour
            "echo": False  # Set to True for SQL debugging
        }
        logger.info("Configuring PostgreSQL database")
        
    else:
        # Default configuration for other databases
        engine_kwargs = {"echo": False}
        logger.warning(f"Unknown database type in URL: {db_url}")
    
    return create_engine(db_url, **engine_kwargs)

# Create database engine and session factory
engine = create_database_engine()
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# SQLAlchemy declarative base
Base = declarative_base()

def get_db():
    """
    Dependency function to provide database sessions.
    Automatically handles session lifecycle and cleanup.
    """
    db = SessionLocal()
    try:
        yield db
    except Exception as e:
        logger.error(f"Database session error: {e}")
        db.rollback()
        raise
    finally:
        db.close()

def test_database_connection():
    """
    Test database connectivity on startup.
    Returns True if successful, False otherwise.
    """
    try:
        from sqlalchemy import text
        with engine.connect() as connection:
            result = connection.execute(text("SELECT 1"))
            result.fetchone()
        logger.info(f"Database connection successful: {Config.DB_URL}")
        return True
    except Exception as e:
        logger.error(f"Database connection failed: {e}")
        return False