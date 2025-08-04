"""
Database connection and utilities for La Factoria
Simple database setup using SQLAlchemy with Railway PostgreSQL
"""

from sqlalchemy import create_engine, MetaData
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
import logging

from .config import settings

logger = logging.getLogger(__name__)

# SQLAlchemy setup
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
            connection.execute("SELECT 1")
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
            # Get database version and basic info
            result = connection.execute("SELECT version()").fetchone()
            version = result[0] if result else "Unknown"

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
        Run a SQL migration file

        Args:
            migration_file: Path to the SQL migration file
        """
        try:
            with open(migration_file, 'r') as f:
                migration_sql = f.read()

            with engine.connect() as connection:
                # Split on semicolons and execute each statement
                statements = [stmt.strip() for stmt in migration_sql.split(';') if stmt.strip()]

                for statement in statements:
                    if statement:
                        connection.execute(statement)

                connection.commit()

            logger.info(f"Migration {migration_file} executed successfully")

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
                        result = connection.execute(table_stats_query)
                        for row in result:
                            stats[row[0]] = {"row_count": row[1]}
                    except:
                        # Fallback for basic stats
                        stats = {"note": "Table statistics not available"}
                else:
                    # SQLite version
                    tables = ['users', 'educational_content', 'quality_assessments']
                    for table in tables:
                        try:
                            result = connection.execute(f"SELECT COUNT(*) FROM {table}").fetchone()
                            stats[table] = {"row_count": result[0] if result else 0}
                        except:
                            stats[table] = {"row_count": 0, "error": "Table may not exist"}

                return stats

        except Exception as e:
            logger.error(f"Failed to get table stats: {e}")
            return {"error": str(e)}
