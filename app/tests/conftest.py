import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.core.config import settings
from app.db.base import Base
from app.main import app
from app.db.session import get_db

@pytest.fixture(scope="session")
def db_engine():
    # Use the main database URL directly
    engine = create_engine(settings.database_url, connect_args={"options": "-csearch_path=public"})
    yield engine

@pytest.fixture(scope="function")
def db(db_engine):
    # Create a new connection and transaction
    connection = db_engine.connect()
    # Start a new nested transaction (SAVEPOINT)
    transaction = connection.begin()
    
    # Bind the session to the connection
    SessionLocal = sessionmaker(bind=connection)
    db = SessionLocal()

    yield db

    # Rollback the transaction after the test
    db.close()
    transaction.rollback()
    connection.close()

@pytest.fixture(scope="function")
def client(db):
    def override_get_db():
        try:
            yield db
        finally:
            pass

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as c:
        yield c
    app.dependency_overrides.clear()

@pytest.fixture(scope="function")
def authenticated_client(client, user):
    from app.services.auth import get_current_user
    
    original_dependency = app.dependency_overrides.get(get_current_user, None)
    app.dependency_overrides[get_current_user] = lambda: user
    
    try:
        yield client
    finally:
        if original_dependency:
            app.dependency_overrides[get_current_user] = original_dependency
        else:
            del app.dependency_overrides[get_current_user]