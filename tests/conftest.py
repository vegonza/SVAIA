import os
import tempfile
from datetime import datetime, timezone
from uuid import uuid4

import pytest
from flask import Flask
from flask_login import LoginManager

from app import app as flask_app
from services.auth.password_utils import hash as hash_password
from services.sql.models import Project, User, db


@pytest.fixture(scope='function')
def app():
    """Create and configure a new app instance for each test."""
    # Create a temporary file to serve as the database
    db_fd, db_path = tempfile.mkstemp()

    # Configure the app for testing
    flask_app.config.update({
        'TESTING': True,
        'SQLALCHEMY_DATABASE_URI': f'sqlite:///{db_path}',
        'SECRET_KEY': 'test-secret-key',
        'WTF_CSRF_ENABLED': False,
        'LOGIN_DISABLED': False
    })

    # Create the database and the database table
    with flask_app.app_context():
        # Drop all tables first to ensure clean state
        db.drop_all()
        db.create_all()

        # Create a test user
        test_user = User(
            name='testuser',
            last_name='Test',
            email='test@example.com',
            password=hash_password('testpassword'),
            is_admin=False
        )
        db.session.add(test_user)

        # Create an admin user
        admin_user = User(
            name='admin',
            last_name='Admin',
            email='admin@example.com',
            password=hash_password('adminpassword'),
            is_admin=True
        )
        db.session.add(admin_user)

        db.session.commit()

    yield flask_app

    # Clean up
    with flask_app.app_context():
        db.session.remove()
        db.drop_all()

    os.close(db_fd)
    os.unlink(db_path)


@pytest.fixture
def client(app):
    """A test client for the app."""
    return app.test_client()


@pytest.fixture
def runner(app):
    """A test runner for the app's Click commands."""
    return app.test_cli_runner()


@pytest.fixture
def test_user():
    """Test user data."""
    return {
        'name': 'testuser',
        'password': 'testpassword',
        'email': 'test@example.com'
    }


@pytest.fixture
def admin_user():
    """Admin user data."""
    return {
        'name': 'admin',
        'password': 'adminpassword',
        'email': 'admin@example.com'
    }


@pytest.fixture
def invalid_user():
    """Invalid user data for testing failed authentication."""
    return {
        'name': 'nonexistent',
        'password': 'wrongpassword'
    }


@pytest.fixture
def test_user_db(app):
    """Test user database object."""
    with app.app_context():
        user = User.query.filter_by(name='testuser').first()
        return user


@pytest.fixture
def admin_user_db(app):
    """Admin user database object."""
    with app.app_context():
        user = User.query.filter_by(name='admin').first()
        return user


@pytest.fixture
def test_project(app, test_user_db):
    """Test project fixture."""
    with app.app_context():
        project = Project(
            uuid=str(uuid4()),
            name='Test Project',
            description='A test project for testing',
            total_vulnerabilities_criteria='10',
            solvability_criteria='high',
            max_vulnerability_level='critical',
            user_id=test_user_db.id
        )
        # Manually set timestamps to avoid UTC issue
        project.created_at = datetime.now(timezone.utc)
        project.updated_at = datetime.now(timezone.utc)

        db.session.add(project)
        db.session.commit()

        # Refresh the object to ensure it's attached to the session
        db.session.refresh(project)
        return project
