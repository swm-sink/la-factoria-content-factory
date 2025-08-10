"""
Test Dependency Compatibility
=============================

TDD approach to ensure all dependencies are compatible and properly versioned.
"""

import sys
import pytest
import importlib.metadata as metadata
from packaging import version


class TestDependencyVersions:
    """Test that all critical dependencies are at compatible versions"""
    
    def test_fastapi_version_compatibility(self):
        """Ensure FastAPI version is compatible with requirements"""
        fastapi_version = metadata.version('fastapi')
        assert version.parse(fastapi_version) >= version.parse('0.104.0'), \
            f"FastAPI version {fastapi_version} is too old"
        assert version.parse(fastapi_version) < version.parse('0.120.0'), \
            f"FastAPI version {fastapi_version} may have breaking changes"
    
    def test_pydantic_v2_installed(self):
        """Ensure Pydantic v2 is installed (not v1)"""
        pydantic_version = metadata.version('pydantic')
        assert version.parse(pydantic_version) >= version.parse('2.0.0'), \
            f"Pydantic v1 detected ({pydantic_version}), v2 required"
        assert version.parse(pydantic_version) < version.parse('3.0.0'), \
            f"Pydantic v3 not yet supported"
    
    def test_uvicorn_version_compatibility(self):
        """Ensure uvicorn version is compatible"""
        uvicorn_version = metadata.version('uvicorn')
        assert version.parse(uvicorn_version) >= version.parse('0.24.0'), \
            f"Uvicorn version {uvicorn_version} is too old"
    
    def test_sqlalchemy_v2_installed(self):
        """Ensure SQLAlchemy 2.0+ is installed"""
        sqlalchemy_version = metadata.version('sqlalchemy')
        assert version.parse(sqlalchemy_version) >= version.parse('2.0.0'), \
            f"SQLAlchemy 2.0+ required, found {sqlalchemy_version}"
    
    def test_critical_dependencies_present(self):
        """Ensure all critical dependencies are installed"""
        critical_deps = [
            'fastapi',
            'pydantic',
            'pydantic-settings',
            'uvicorn',
            'sqlalchemy',
            'asyncpg',
            'psycopg2-binary',
            'alembic',
            'redis',
            'slowapi',
            'openai',
            'anthropic',
            'pytest',
            'pytest-asyncio'
        ]
        
        for dep in critical_deps:
            try:
                version = metadata.version(dep)
                assert version is not None, f"{dep} not installed"
            except metadata.PackageNotFoundError:
                pytest.fail(f"Critical dependency {dep} not found")
    
    def test_no_conflicting_dependencies(self):
        """Check for known conflicting dependencies"""
        # Check that we don't have both psycopg2 and psycopg2-binary
        try:
            metadata.version('psycopg2')
            metadata.version('psycopg2-binary')
            pytest.fail("Both psycopg2 and psycopg2-binary installed - conflict!")
        except metadata.PackageNotFoundError:
            pass  # One missing is fine
    
    def test_python_version_compatibility(self):
        """Ensure Python version is compatible"""
        python_version = sys.version_info
        assert python_version >= (3, 11), \
            f"Python 3.11+ required, found {python_version.major}.{python_version.minor}"
        # Note: Python 3.13 may have compatibility issues
        if python_version >= (3, 13):
            pytest.skip("Python 3.13+ may have compatibility issues - verify manually")


class TestImportCompatibility:
    """Test that all critical imports work correctly"""
    
    def test_fastapi_imports(self):
        """Test FastAPI imports work"""
        from fastapi import FastAPI, APIRouter, Depends, HTTPException
        from fastapi.middleware.cors import CORSMiddleware
        from fastapi.staticfiles import StaticFiles
        assert FastAPI is not None
    
    def test_pydantic_v2_imports(self):
        """Test Pydantic v2 specific imports"""
        from pydantic import BaseModel, Field, ConfigDict
        from pydantic_settings import BaseSettings
        
        # Test v2 specific features
        class TestModel(BaseModel):
            model_config = ConfigDict(from_attributes=True)
            field: str = Field(default="test")
        
        assert TestModel(field="value").field == "value"
    
    def test_sqlalchemy_v2_imports(self):
        """Test SQLAlchemy 2.0 imports"""
        from sqlalchemy import create_engine, select
        from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
        from sqlalchemy.orm import Session, sessionmaker
        assert create_engine is not None
    
    def test_ai_provider_imports(self):
        """Test AI provider SDK imports"""
        import openai
        import anthropic
        assert openai is not None
        assert anthropic is not None
    
    def test_application_imports(self):
        """Test that our application imports work"""
        from src.main import app
        from src.core.config import settings
        from src.services.educational_content_service import EducationalContentService
        assert app is not None
        assert settings is not None
        assert EducationalContentService is not None


class TestFeatureCompatibility:
    """Test that specific features work with current dependencies"""
    
    @pytest.mark.asyncio
    async def test_async_context_manager(self):
        """Test FastAPI lifespan with async context manager"""
        from contextlib import asynccontextmanager
        from fastapi import FastAPI
        
        @asynccontextmanager
        async def lifespan(app: FastAPI):
            # Startup
            yield
            # Shutdown
        
        app = FastAPI(lifespan=lifespan)
        assert app is not None
    
    def test_pydantic_settings_env_loading(self):
        """Test Pydantic Settings can load from environment"""
        from pydantic_settings import BaseSettings
        import os
        
        class TestSettings(BaseSettings):
            test_var: str = "default"
        
        os.environ['TEST_VAR'] = 'from_env'
        settings = TestSettings()
        assert settings.test_var == 'from_env'
        del os.environ['TEST_VAR']
    
    def test_fastapi_dependency_injection(self):
        """Test FastAPI dependency injection works"""
        from fastapi import FastAPI, Depends
        
        def get_db():
            return "database"
        
        app = FastAPI()
        
        @app.get("/test")
        def test_endpoint(db=Depends(get_db)):
            return {"db": db}
        
        assert app is not None