"""Pytest configuration."""

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.database import Base
from app.models import Log, MonitoringRule, Action, AlertHistory


@pytest.fixture(scope="session")
def test_db_engine():
    """Create test database engine."""
    # Use in-memory SQLite for tests
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(bind=engine)
    yield engine
    Base.metadata.drop_all(bind=engine)


@pytest.fixture(scope="function")
def test_db(test_db_engine):
    """Create test database session."""
    TestingSessionLocal = sessionmaker(
        autocommit=False, autoflush=False, bind=test_db_engine
    )
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


@pytest.fixture
def sample_log_data():
    """Sample log data for testing."""
    return {
        "sid": "CA1234567890abcdef1234567890abcdef",
        "from": "+12345678901",
        "to": "+19876543210",
        "status": "completed",
        "duration": 120,
        "start_time": "2024-01-01T12:00:00Z",
        "end_time": "2024-01-01T12:02:00Z",
        "error_code": None,
        "error_message": None,
    }
