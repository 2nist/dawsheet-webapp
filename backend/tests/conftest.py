import sys
from pathlib import Path

# Ensure backend/app is on sys.path so 'app' package imports succeed when running tests from repo root
ROOT = Path(__file__).resolve().parents[2]  # points to webapp/
APP_DIR = ROOT / 'backend' / 'app'
if str(APP_DIR) not in sys.path:
    sys.path.insert(0, str(APP_DIR.parent))  # add backend so 'app' is a package root

# Provide async_client and db_session fixtures if not already defined (reuse existing ones if available)
import pytest
import pytest_asyncio
import asyncio
from fastapi.testclient import TestClient
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.main import app  # type: ignore
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from app.database import Base, get_session  # type: ignore

# Build in-memory SQLite async engine for tests
TEST_DB_URL = "sqlite+aiosqlite:///:memory:"
engine_test = create_async_engine(TEST_DB_URL, future=True)
SessionLocalTest = async_sessionmaker(engine_test, expire_on_commit=False, class_=AsyncSession)

async def override_get_session():
    async with SessionLocalTest() as session:  # type: ignore
        yield session

# Apply dependency override after app import using function object
app.dependency_overrides[get_session] = override_get_session  # type: ignore


@pytest.fixture()
def client():
    return TestClient(app)


@pytest_asyncio.fixture()
async def async_client():
    async with AsyncClient(app=app, base_url="http://test") as ac:
        yield ac


@pytest_asyncio.fixture()
async def db_session() -> AsyncSession:  # type: ignore[return-value]
    # Ensure tables created once
    async with engine_test.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    async with SessionLocalTest() as session:  # type: ignore
        yield session
