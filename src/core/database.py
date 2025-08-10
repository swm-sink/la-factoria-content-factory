"""
Database connection and utilities for La Factoria
Simple database setup using SQLAlchemy with Railway PostgreSQL
"""

from sqlalchemy import create_engine, MetaData, text
from sqlalchemy.orm import declarative_base, sessionmaker
from sqlalchemy.pool import StaticPool
import logging

from .config import settings

logger = logging.getLogger(__name__)

# SQLAlchemy setup - using modern declarative_base from sqlalchemy.orm
Base = declarative_base()
metadata = MetaData()

# Database engine and session configuration
if settings.database_url.startswith("sqlite"):
    # SQLite for development
    engine = create_engine(
        settings.database_url,
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
else:
    # PostgreSQL for production (Railway)
    engine = create_engine(
        settings.database_url,
        pool_size=settings.DB_POOL_SIZE,
        max_overflow=settings.DB_MAX_OVERFLOW,
        pool_timeout=settings.DB_POOL_TIMEOUT,
        pool_recycle=settings.DB_POOL_RECYCLE,
        pool_pre_ping=True,  # Validate connections before use
        echo=settings.DEBUG  # Log SQL queries in debug mode
    )

# Session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def get_database():
    """
    Database dependency for FastAPI endpoints

    Yields a database session and ensures proper cleanup
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Async version for async endpoints
async def get_db():
    """
    Async database dependency for FastAPI async endpoints
    
    Yields a database session and ensures proper cleanup
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

async def init_database():
    """
    Initialize database tables

    Creates all tables defined in models if they don't exist
    """
    try:
        logger.info("Initializing database...")

        # Import models to register them with Base
        from ..models.educational import EducationalContentDB, UserModel

        # Create all tables
        Base.metadata.create_all(bind=engine)

        logger.info("Database initialized successfully")

    except Exception as e:
        logger.error(f"Failed to initialize database: {e}")
        raise

async def check_database_connection():
    """
    Check database connectivity

    Returns True if database is accessible, False otherwise
    """
    try:
        with engine.connect() as connection:
            connection.execute(text("SELECT 1"))
        return True
    except Exception as e:
        logger.error(f"Database connection check failed: {e}")
        return False

async def get_database_info():
    """
    Get database information for health checks
    """
    try:
        with engine.connect() as connection:
            # Get database version and basic info (database-specific)
            if settings.database_url.startswith("sqlite"):
                # SQLite version query
                result = connection.execute(text("SELECT sqlite_version()")).fetchone()
                version = f"SQLite {result[0]}" if result else "SQLite (Unknown version)"
            else:
                # PostgreSQL version query
                result = connection.execute(text("SELECT version()")).fetchone()
                version = result[0] if result else "PostgreSQL (Unknown version)"

            return {
                "status": "healthy",
                "version": version,
                "url": settings.database_url[:20] + "..." if settings.database_url else "Not configured",
                "pool_size": settings.DB_POOL_SIZE,
                "max_overflow": settings.DB_MAX_OVERFLOW
            }

    except Exception as e:
        logger.error(f"Failed to get database info: {e}")
        return {
            "status": "unhealthy",
            "error": str(e),
            "url": settings.database_url[:20] + "..." if settings.database_url else "Not configured"
        }

class DatabaseManager:
    """
    Database management utilities for La Factoria
    """

    @staticmethod
    async def run_migration(migration_file: str):
        """
        Run a SQL migration file with path validation

        Args:
            migration_file: Path to the SQL migration file (must be in migrations directory)
        """
        import os
        from pathlib import Path
        
        try:
            # SECURITY: Validate migration file path to prevent path traversal
            migration_path = Path(migration_file).resolve()
            base_dir = Path(__file__).parent.parent.parent  # Project root
            migrations_dir = base_dir / 'migrations'
            
            # Ensure the file is within the migrations directory
            if not str(migration_path).startswith(str(migrations_dir)):
                raise ValueError(f"Migration file must be in migrations directory: {migration_file}")
            
            # Check if file exists and is a file (not directory)
            if not migration_path.is_file():
                raise FileNotFoundError(f"Migration file not found: {migration_file}")
            
            # Check file extension
            if migration_path.suffix.lower() not in ['.sql', '.psql']:
                raise ValueError(f"Invalid migration file type: {migration_path.suffix}")
            
            with open(migration_path, 'r') as f:
                migration_sql = f.read()

            with engine.connect() as connection:
                # Split on semicolons and execute each statement
                statements = [stmt.strip() for stmt in migration_sql.split(';') if stmt.strip()]

                for statement in statements:
                    if statement:
                        connection.execute(text(statement))

                connection.commit()

            logger.info(f"Migration {migration_path.name} executed successfully")

        except Exception as e:
            logger.error(f"Migration {migration_file} failed: {e}")
            raise

    @staticmethod
    async def backup_database(backup_file: str):
        """
        Create a database backup (basic implementation)
        """
        # Placeholder - would implement actual backup logic
        logger.info(f"Database backup to {backup_file} - not implemented")

    @staticmethod
    async def get_table_stats():
        """
        Get statistics about database tables
        """
        try:
            with engine.connect() as connection:
                stats = {}

                # Get table sizes (PostgreSQL specific)
                if not settings.database_url.startswith("sqlite"):
                    table_stats_query = """
                    SELECT
                        table_name,
                        (xpath('/row/count/text()', xml_count))[1]::text::int as row_count
                    FROM (
                        SELECT
                            table_name,
                            query_to_xml(format('select count(*) as count from %I.%I',
                                table_schema, table_name), false, true, '') as xml_count
                        FROM information_schema.tables
                        WHERE table_schema = 'public'
                        AND table_type = 'BASE TABLE'
                    ) t;
                    """

                    try:
                        result = connection.execute(text(table_stats_query))
                        for row in result:
                            stats[row[0]] = {"row_count": row[1]}
                    except:
                        # Fallback for basic stats
                        stats = {"note": "Table statistics not available"}
                else:
                    # SQLite version - use whitelist with safe queries
                    # SECURITY: Using explicit queries instead of string interpolation
                    # to prevent SQL injection attacks
                    safe_queries = {
                        'users': "SELECT COUNT(*) FROM users",
                        'educational_content': "SELECT COUNT(*) FROM educational_content",
                        'quality_assessments': "SELECT COUNT(*) FROM quality_assessments"
                    }
                    
                    for table_name, query in safe_queries.items():
                        try:
                            result = connection.execute(text(query)).fetchone()
                            stats[table_name] = {"row_count": result[0] if result else 0}
                        except:
                            stats[table_name] = {"row_count": 0, "error": "Table may not exist"}

                return stats

        except Exception as e:
            logger.error(f"Failed to get table stats: {e}")
            return {"error": str(e)}

# FastAPI dependency for database sessions
async def get_db():
    """
    FastAPI dependency for getting database sessions
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
