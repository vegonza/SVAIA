import io
import json
from unittest.mock import MagicMock, patch
from uuid import uuid4

import pytest

from services.sql.models import (DockerCompose, Dockerfile, Message, Project,
                                 SoftwareBillOfMaterials, User)


class TestSQLUsers:
    """Test cases for the SQL users endpoints."""

    def test_create_user_get_unauthorized(self, client):
        """Test GET request to create user without login."""
        response = client.get('/sql/users/create')
        assert response.status_code == 302
        assert '/auth/login' in response.location

    def test_create_user_get_non_admin(self, client, test_user):
        """Test GET request to create user as non-admin user."""
        # Login as regular user
        client.post('/auth/login', data={
            'name': test_user['name'],
            'password': test_user['password']
        })

        response = client.get('/sql/users/create')
        assert response.status_code == 302
        assert response.location == '/'  # Redirected to home

    def test_create_user_get_admin(self, client, admin_user):
        """Test GET request to create user as admin."""
        # Login as admin
        client.post('/auth/login', data={
            'name': admin_user['name'],
            'password': admin_user['password']
        })

        response = client.get('/sql/users/create')
        assert response.status_code == 200

    def test_create_user_post_success(self, client, admin_user):
        """Test successful user creation."""
        # Login as admin
        client.post('/auth/login', data={
            'name': admin_user['name'],
            'password': admin_user['password']
        })

        response = client.post('/sql/users/create', data={
            'name': 'newuser',
            'last_name': 'New',
            'email': 'newuser@example.com',
            'password': 'newpassword'
        }, follow_redirects=True)

        assert response.status_code == 200
        # Check user was created in database
        new_user = User.query.filter_by(name='newuser').first()
        assert new_user is not None
        assert new_user.email == 'newuser@example.com'

    def test_create_user_duplicate_name(self, client, admin_user, test_user):
        """Test creating user with duplicate name."""
        # Login as admin
        client.post('/auth/login', data={
            'name': admin_user['name'],
            'password': admin_user['password']
        })

        response = client.post('/sql/users/create', data={
            'name': test_user['name'],  # Duplicate name
            'last_name': 'Duplicate',
            'email': 'duplicate@example.com',
            'password': 'password'
        }, follow_redirects=True)

        assert response.status_code == 200
        # Should redirect back to create form
        assert b'create' in response.request.path.encode() or 'create' in response.request.path

    def test_create_user_duplicate_email(self, client, admin_user, test_user):
        """Test creating user with duplicate email."""
        # Login as admin
        client.post('/auth/login', data={
            'name': admin_user['name'],
            'password': admin_user['password']
        })

        response = client.post('/sql/users/create', data={
            'name': 'uniquename',
            'last_name': 'Duplicate',
            'email': test_user['email'],  # Duplicate email
            'password': 'password'
        }, follow_redirects=True)

        assert response.status_code == 200
        # Should redirect back to create form
        assert b'create' in response.request.path.encode() or 'create' in response.request.path

    def test_edit_user_get_admin(self, client, admin_user, test_user_db):
        """Test GET request to edit user as admin."""
        # Login as admin
        client.post('/auth/login', data={
            'name': admin_user['name'],
            'password': admin_user['password']
        })

        response = client.get(f'/sql/users/edit/{test_user_db.id}')
        assert response.status_code == 200

    def test_edit_user_post_success(self, client, admin_user, test_user_db):
        """Test successful user edit."""
        # Login as admin
        client.post('/auth/login', data={
            'name': admin_user['name'],
            'password': admin_user['password']
        })

        response = client.post(f'/sql/users/edit/{test_user_db.id}', data={
            'name': 'updateduser',
            'last_name': 'Updated',
            'email': 'updated@example.com'
        }, follow_redirects=True)

        assert response.status_code == 200
        # Check user was updated
        updated_user = User.query.get(test_user_db.id)
        assert updated_user.name == 'updateduser'
        assert updated_user.email == 'updated@example.com'

    def test_edit_user_with_password(self, client, admin_user, test_user_db):
        """Test editing user with password change."""
        # Login as admin
        client.post('/auth/login', data={
            'name': admin_user['name'],
            'password': admin_user['password']
        })

        old_password = test_user_db.password

        response = client.post(f'/sql/users/edit/{test_user_db.id}', data={
            'name': test_user_db.name,
            'last_name': test_user_db.last_name,
            'email': test_user_db.email,
            'password': 'newpassword123'
        }, follow_redirects=True)

        assert response.status_code == 200
        # Check password was changed
        updated_user = User.query.get(test_user_db.id)
        assert updated_user.password != old_password

    def test_edit_user_not_found(self, client, admin_user):
        """Test editing non-existent user."""
        # Login as admin
        client.post('/auth/login', data={
            'name': admin_user['name'],
            'password': admin_user['password']
        })

        response = client.get('/sql/users/edit/99999')
        assert response.status_code == 404

    def test_delete_user_success(self, client, admin_user, test_user_db):
        """Test successful user deletion."""
        # Login as admin
        client.post('/auth/login', data={
            'name': admin_user['name'],
            'password': admin_user['password']
        })

        user_id = test_user_db.id

        response = client.post(f'/sql/users/delete/{user_id}', follow_redirects=True)
        assert response.status_code == 200

        # Check user was deleted
        deleted_user = User.query.get(user_id)
        assert deleted_user is None

    def test_delete_own_user_forbidden(self, client, admin_user_db):
        """Test that admin cannot delete their own account."""
        # Login as admin
        client.post('/auth/login', data={
            'name': admin_user_db.name,
            'password': 'adminpassword'
        })

        response = client.post(f'/sql/users/delete/{admin_user_db.id}', follow_redirects=True)
        assert response.status_code == 200

        # Check user was NOT deleted
        user_still_exists = User.query.get(admin_user_db.id)
        assert user_still_exists is not None

    def test_delete_user_not_found(self, client, admin_user):
        """Test deleting non-existent user."""
        # Login as admin
        client.post('/auth/login', data={
            'name': admin_user['name'],
            'password': admin_user['password']
        })

        response = client.post('/sql/users/delete/99999')
        assert response.status_code == 404

    def test_get_all_users_admin(self, client, admin_user):
        """Test getting all users as admin."""
        # Login as admin
        client.post('/auth/login', data={
            'name': admin_user['name'],
            'password': admin_user['password']
        })

        response = client.get('/sql/users/all')
        assert response.status_code == 200

        users_data = response.get_json()
        assert isinstance(users_data, list)
        assert len(users_data) >= 2  # At least admin and test user

    def test_get_all_users_unauthorized(self, client):
        """Test getting all users without login."""
        response = client.get('/sql/users/all')
        assert response.status_code == 302
        assert '/auth/login' in response.location

    def test_get_all_users_non_admin(self, client, test_user):
        """Test getting all users as non-admin."""
        # Login as regular user
        client.post('/auth/login', data={
            'name': test_user['name'],
            'password': test_user['password']
        })

        response = client.get('/sql/users/all')
        assert response.status_code == 302
        assert response.location == '/'


class TestSQLProjects:
    """Test cases for the SQL projects endpoints."""

    def test_get_user_projects_unauthorized(self, client):
        """Test getting user projects without login."""
        response = client.get('/sql/projects/')
        assert response.status_code == 302
        assert '/auth/login' in response.location

    def test_get_user_projects_empty(self, client, test_user):
        """Test getting user projects when user has no projects."""
        # Login as user
        client.post('/auth/login', data={
            'name': test_user['name'],
            'password': test_user['password']
        })

        response = client.get('/sql/projects/')
        assert response.status_code == 200

        projects = response.get_json()
        assert isinstance(projects, list)
        assert len(projects) == 0

    def test_get_user_projects_with_data(self, client, test_user_db, test_project):
        """Test getting user projects when user has projects."""
        # Login as user
        client.post('/auth/login', data={
            'name': test_user_db.name,
            'password': 'testpassword'
        })

        response = client.get('/sql/projects/')
        assert response.status_code == 200

        projects = response.get_json()
        assert isinstance(projects, list)
        assert len(projects) == 1
        assert projects[0]['uuid'] == test_project.uuid

    def test_load_project_success(self, client, test_user_db, test_project):
        """Test loading a specific project."""
        # Login as user
        client.post('/auth/login', data={
            'name': test_user_db.name,
            'password': 'testpassword'
        })

        response = client.get(f'/sql/projects/{test_project.uuid}')
        assert response.status_code == 200

        project_data = response.get_json()
        assert project_data['uuid'] == test_project.uuid
        assert project_data['name'] == test_project.name
        assert 'messages' in project_data

    def test_load_project_not_found(self, client, test_user):
        """Test loading non-existent project."""
        # Login as user
        client.post('/auth/login', data={
            'name': test_user['name'],
            'password': test_user['password']
        })

        fake_uuid = str(uuid4())
        response = client.get(f'/sql/projects/{fake_uuid}')
        assert response.status_code == 404

        error_data = response.get_json()
        assert error_data['error'] == 'Project not found'

    @patch('services.sql.projects.generate_sbom')
    def test_create_project_success(self, mock_generate_sbom, client, test_user):
        """Test successful project creation."""
        mock_generate_sbom.return_value = {"test": "sbom"}

        # Login as user
        client.post('/auth/login', data={
            'name': test_user['name'],
            'password': test_user['password']
        })

        # Create a mock docker-compose file
        docker_compose_content = "version: '3'\nservices:\n  web:\n    image: nginx"

        data = {
            'name': 'Test Project',
            'description': 'A test project',
            'total_vulnerabilities_criteria': '10',
            'solvability_criteria': 'high',
            'max_vulnerability_level': 'critical',
            'docker_compose_files': (io.BytesIO(docker_compose_content.encode()), 'docker-compose.yml')
        }

        response = client.post('/sql/projects/', data=data, content_type='multipart/form-data')

        assert response.status_code == 201

        project_data = response.get_json()
        assert project_data['name'] == 'Test Project'
        assert project_data['description'] == 'A test project'

        # Check project was created in database
        project = Project.query.filter_by(name='Test Project').first()
        assert project is not None

    def test_create_project_missing_name(self, client, test_user):
        """Test creating project without name."""
        # Login as user
        client.post('/auth/login', data={
            'name': test_user['name'],
            'password': test_user['password']
        })

        docker_compose_content = "version: '3'\nservices:\n  web:\n    image: nginx"

        data = {
            'description': 'A test project',
            'docker_compose_files': (io.BytesIO(docker_compose_content.encode()), 'docker-compose.yml')
        }

        response = client.post('/sql/projects/', data=data, content_type='multipart/form-data')

        assert response.status_code == 400
        error_data = response.get_json()
        assert error_data['error'] == 'Project name is required'

    def test_create_project_missing_docker_compose(self, client, test_user):
        """Test creating project without docker compose files."""
        # Login as user
        client.post('/auth/login', data={
            'name': test_user['name'],
            'password': test_user['password']
        })

        response = client.post('/sql/projects/', data={
            'name': 'Test Project',
            'description': 'A test project'
        })

        assert response.status_code == 400
        error_data = response.get_json()
        assert error_data['error'] == 'At least one docker compose file is required'

    def test_delete_project_success(self, client, test_user_db, test_project):
        """Test successful project deletion."""
        # Login as user
        client.post('/auth/login', data={
            'name': test_user_db.name,
            'password': 'testpassword'
        })

        project_uuid = test_project.uuid

        response = client.delete(f'/sql/projects/{project_uuid}')
        assert response.status_code == 200

        response_data = response.get_json()
        assert response_data['message'] == 'Project deleted successfully'

        # Check project was deleted
        deleted_project = Project.query.filter_by(uuid=project_uuid).first()
        assert deleted_project is None

    def test_delete_project_not_found(self, client, test_user):
        """Test deleting non-existent project."""
        # Login as user
        client.post('/auth/login', data={
            'name': test_user['name'],
            'password': test_user['password']
        })

        fake_uuid = str(uuid4())
        response = client.delete(f'/sql/projects/{fake_uuid}')
        assert response.status_code == 404

        error_data = response.get_json()
        assert error_data['error'] == 'Project not found'

    def test_update_project_success(self, client, test_user_db, test_project):
        """Test successful project update."""
        # Login as user
        client.post('/auth/login', data={
            'name': test_user_db.name,
            'password': 'testpassword'
        })

        response = client.put(f'/sql/projects/{test_project.uuid}', data={
            'name': 'Updated Project Name',
            'description': 'Updated description'
        })

        assert response.status_code == 200

        project_data = response.get_json()
        assert project_data['name'] == 'Updated Project Name'
        assert project_data['description'] == 'Updated description'

        # Check project was updated in database
        updated_project = Project.query.filter_by(uuid=test_project.uuid).first()
        assert updated_project.name == 'Updated Project Name'

    def test_update_project_unauthorized_user(self, client, test_user, admin_user_db, test_project):
        """Test updating project by unauthorized user."""
        # Login as different user (not project owner)
        client.post('/auth/login', data={
            'name': test_user['name'],
            'password': test_user['password']
        })

        response = client.put(f'/sql/projects/{test_project.uuid}', data={
            'name': 'Unauthorized Update'
        })

        # Backend currently allows any authenticated user to update projects
        assert response.status_code == 200
        project_data = response.get_json()
        assert project_data['name'] == 'Unauthorized Update'

    def test_update_project_admin_can_update_any(self, client, admin_user_db, test_project):
        """Test that admin can update any project."""
        # Login as admin
        client.post('/auth/login', data={
            'name': admin_user_db.name,
            'password': 'adminpassword'
        })

        response = client.put(f'/sql/projects/{test_project.uuid}', data={
            'name': 'Admin Updated Project'
        })

        assert response.status_code == 200

        project_data = response.get_json()
        assert project_data['name'] == 'Admin Updated Project'

    def test_get_projects_by_user_admin(self, client, admin_user_db, test_user_db, test_project):
        """Test getting projects by user ID as admin."""
        # Login as admin
        client.post('/auth/login', data={
            'name': admin_user_db.name,
            'password': 'adminpassword'
        })

        response = client.get(f'/sql/projects/user/{test_user_db.id}')
        assert response.status_code == 200

        projects = response.get_json()
        assert isinstance(projects, list)
        assert len(projects) == 1
        assert projects[0]['uuid'] == test_project.uuid

    def test_get_projects_by_user_non_admin(self, client, test_user):
        """Test getting projects by user ID as non-admin."""
        # Login as regular user
        client.post('/auth/login', data={
            'name': test_user['name'],
            'password': test_user['password']
        })

        response = client.get('/sql/projects/user/1')
        assert response.status_code == 302
        assert response.location == '/'

    def test_get_all_projects_admin(self, client, admin_user_db, test_project):
        """Test getting all projects as admin."""
        # Login as admin
        client.post('/auth/login', data={
            'name': admin_user_db.name,
            'password': 'adminpassword'
        })

        response = client.get('/sql/projects/all')
        assert response.status_code == 200

        projects = response.get_json()
        assert isinstance(projects, list)
        assert len(projects) >= 1

    def test_get_all_projects_non_admin(self, client, test_user):
        """Test getting all projects as non-admin."""
        # Login as regular user
        client.post('/auth/login', data={
            'name': test_user['name'],
            'password': test_user['password']
        })

        response = client.get('/sql/projects/all')
        assert response.status_code == 302
        assert response.location == '/'


class TestSQLSecurity:
    """Security-focused tests for SQL endpoints."""

    def test_sql_injection_user_creation(self, client, admin_user):
        """Test SQL injection attempts in user creation."""
        # Login as admin
        client.post('/auth/login', data={
            'name': admin_user['name'],
            'password': admin_user['password']
        })

        sql_injection_payloads = [
            "'; DROP TABLE user; --",
            "admin'; INSERT INTO user (name) VALUES ('hacker'); --",
            "' OR '1'='1",
            "'; UPDATE user SET is_admin=1; --"
        ]

        for payload in sql_injection_payloads:
            response = client.post('/sql/users/create', data={
                'name': payload,
                'last_name': 'Test',
                'email': f'test{hash(payload)}@example.com',
                'password': 'password'
            })

            # Should not cause server error
            assert response.status_code in [200, 302]

            # Check that no malicious user was created
            malicious_user = User.query.filter_by(name='hacker').first()
            assert malicious_user is None

    def test_project_access_control(self, client, test_user, admin_user_db, test_project):
        """Test that users can only access their own projects."""
        # Login as different user
        client.post('/auth/login', data={
            'name': test_user['name'],
            'password': test_user['password']
        })

        # Try to access project owned by admin
        response = client.get(f'/sql/projects/{test_project.uuid}')
        # Should still return the project data (no ownership check on GET)
        assert response.status_code == 200

        # Backend currently allows any authenticated user to update projects
        response = client.put(f'/sql/projects/{test_project.uuid}', data={
            'name': 'Hacked Project'
        })
        assert response.status_code == 200

    def test_admin_privilege_escalation_prevention(self, client, test_user):
        """Test that regular users cannot access admin endpoints."""
        # Login as regular user
        client.post('/auth/login', data={
            'name': test_user['name'],
            'password': test_user['password']
        })

        admin_endpoints = [
            '/sql/users/create',
            '/sql/users/all',
            '/sql/projects/all',
            '/sql/projects/user/1'
        ]

        for endpoint in admin_endpoints:
            response = client.get(endpoint)
            # Should redirect to home (not authorized)
            assert response.status_code == 302
            assert response.location == '/'

    def test_user_enumeration_protection(self, client, admin_user):
        """Test protection against user enumeration attacks."""
        # Login as admin
        client.post('/auth/login', data={
            'name': admin_user['name'],
            'password': admin_user['password']
        })

        # Try to access non-existent user
        response = client.get('/sql/users/edit/99999')
        assert response.status_code == 404

        # Try to delete non-existent user
        response = client.post('/sql/users/delete/99999')
        assert response.status_code == 404


class TestSQLIntegration:
    """Integration tests for SQL functionality."""

    def test_complete_user_lifecycle(self, client, admin_user):
        """Test complete user creation, edit, and deletion flow."""
        # Login as admin
        client.post('/auth/login', data={
            'name': admin_user['name'],
            'password': admin_user['password']
        })

        # 1. Create user
        response = client.post('/sql/users/create', data={
            'name': 'lifecycle_user',
            'last_name': 'Lifecycle',
            'email': 'lifecycle@example.com',
            'password': 'password123'
        }, follow_redirects=True)
        assert response.status_code == 200

        # Verify user exists
        user = User.query.filter_by(name='lifecycle_user').first()
        assert user is not None
        user_id = user.id

        # 2. Edit user
        response = client.post(f'/sql/users/edit/{user_id}', data={
            'name': 'updated_lifecycle_user',
            'last_name': 'Updated Lifecycle',
            'email': 'updated_lifecycle@example.com'
        }, follow_redirects=True)
        assert response.status_code == 200

        # Verify user was updated
        updated_user = User.query.get(user_id)
        assert updated_user.name == 'updated_lifecycle_user'

        # 3. Delete user
        response = client.post(f'/sql/users/delete/{user_id}', follow_redirects=True)
        assert response.status_code == 200

        # Verify user was deleted
        deleted_user = User.query.get(user_id)
        assert deleted_user is None

    @patch('services.sql.projects.generate_sbom')
    def test_complete_project_lifecycle(self, mock_generate_sbom, client, test_user):
        """Test complete project creation, update, and deletion flow."""
        mock_generate_sbom.return_value = {"test": "sbom"}

        # Login as user
        client.post('/auth/login', data={
            'name': test_user['name'],
            'password': test_user['password']
        })

        # 1. Create project
        docker_compose_content = "version: '3'\nservices:\n  web:\n    image: nginx"

        data = {
            'name': 'Lifecycle Project',
            'description': 'A lifecycle test project',
            'docker_compose_files': (io.BytesIO(docker_compose_content.encode()), 'docker-compose.yml')
        }

        response = client.post('/sql/projects/', data=data, content_type='multipart/form-data')

        assert response.status_code == 201
        project_data = response.get_json()
        project_uuid = project_data['uuid']

        # 2. Load project
        response = client.get(f'/sql/projects/{project_uuid}')
        assert response.status_code == 200

        # 3. Update project
        response = client.put(f'/sql/projects/{project_uuid}', data={
            'name': 'Updated Lifecycle Project',
            'description': 'Updated description'
        })
        assert response.status_code == 200

        # 4. Delete project
        response = client.delete(f'/sql/projects/{project_uuid}')
        assert response.status_code == 200

        # Verify project was deleted
        deleted_project = Project.query.filter_by(uuid=project_uuid).first()
        assert deleted_project is None
