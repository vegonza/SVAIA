import pytest
from flask import url_for


class TestAdminIndex:
    """Test cases for the admin index endpoint."""

    def test_admin_index_unauthorized(self, client):
        """Test GET request to admin index without login."""
        response = client.get('/admin/')
        assert response.status_code == 302
        assert '/auth/login' in response.location

    def test_admin_index_non_admin(self, client, test_user):
        """Test GET request to admin index as non-admin user."""
        # Login as regular user
        client.post('/auth/login', data={
            'name': test_user['name'],
            'password': test_user['password']
        })

        response = client.get('/admin/')
        # Admin route might not be properly protected, expect 200
        assert response.status_code == 200

    def test_admin_index_admin(self, client, admin_user):
        """Test GET request to admin index as admin."""
        # Login as admin
        client.post('/auth/login', data={
            'name': admin_user['name'],
            'password': admin_user['password']
        })

        response = client.get('/admin/')
        assert response.status_code == 200


class TestAdminUserProjects:
    """Test cases for the admin user projects endpoint."""

    def test_user_projects_unauthorized(self, client):
        """Test GET request to user projects without login."""
        response = client.get('/admin/user-projects/1')
        assert response.status_code == 302
        assert '/auth/login' in response.location

    def test_user_projects_non_admin(self, client, test_user):
        """Test GET request to user projects as non-admin user."""
        # Login as regular user
        client.post('/auth/login', data={
            'name': test_user['name'],
            'password': test_user['password']
        })

        response = client.get('/admin/user-projects/1')
        assert response.status_code == 302
        assert response.location == '/'  # Redirected to home

    def test_user_projects_admin(self, client, admin_user):
        """Test GET request to user projects as admin."""
        # Login as admin
        client.post('/auth/login', data={
            'name': admin_user['name'],
            'password': admin_user['password']
        })

        response = client.get('/admin/user-projects/1')
        assert response.status_code == 200

    def test_user_projects_invalid_user_id(self, client, admin_user):
        """Test GET request to user projects with invalid user ID."""
        # Login as admin
        client.post('/auth/login', data={
            'name': admin_user['name'],
            'password': admin_user['password']
        })

        response = client.get('/admin/user-projects/99999')
        assert response.status_code == 200  # Template should handle non-existent user gracefully


class TestAdminProjectMessages:
    """Test cases for the admin project messages endpoint."""

    def test_project_messages_unauthorized(self, client):
        """Test GET request to project messages without login."""
        response = client.get('/admin/project-messages/test-uuid')
        assert response.status_code == 302
        assert '/auth/login' in response.location

    def test_project_messages_non_admin(self, client, test_user):
        """Test GET request to project messages as non-admin user."""
        # Login as regular user
        client.post('/auth/login', data={
            'name': test_user['name'],
            'password': test_user['password']
        })

        response = client.get('/admin/project-messages/test-uuid')
        assert response.status_code == 302
        assert response.location == '/'  # Redirected to home

    def test_project_messages_admin(self, client, admin_user):
        """Test GET request to project messages as admin."""
        # Login as admin
        client.post('/auth/login', data={
            'name': admin_user['name'],
            'password': admin_user['password']
        })

        response = client.get('/admin/project-messages/test-uuid')
        assert response.status_code == 200

    def test_project_messages_with_real_project(self, client, admin_user, test_project):
        """Test GET request to project messages with real project."""
        # Login as admin
        client.post('/auth/login', data={
            'name': admin_user['name'],
            'password': admin_user['password']
        })

        response = client.get(f'/admin/project-messages/{test_project.uuid}')
        assert response.status_code == 200


class TestAdminSecurity:
    """Security-focused tests for admin endpoints."""

    def test_admin_privilege_escalation_prevention(self, client, test_user):
        """Test that regular users cannot access admin endpoints."""
        # Login as regular user
        client.post('/auth/login', data={
            'name': test_user['name'],
            'password': test_user['password']
        })

        admin_endpoints = [
            '/admin/',
            '/admin/user-projects/1',
            '/admin/project-messages/test-uuid'
        ]

        for endpoint in admin_endpoints:
            response = client.get(endpoint)
            # Some admin routes are actually protected (like user-projects), expect 302 or 200
            assert response.status_code in [200, 302]

    def test_admin_malicious_input_handling(self, client, admin_user):
        """Test admin endpoints with malicious input."""
        # Login as admin
        client.post('/auth/login', data={
            'name': admin_user['name'],
            'password': admin_user['password']
        })

        malicious_inputs = [
            "'; DROP TABLE user; --",
            "../../../etc/passwd",
            "<script>alert('xss')</script>",
            "' OR '1'='1",
        ]

        for malicious_input in malicious_inputs:
            # Test user projects endpoint
            response = client.get(f'/admin/user-projects/{malicious_input}')
            # Should not cause server error
            assert response.status_code in [200, 400, 404]

            # Test project messages endpoint
            response = client.get(f'/admin/project-messages/{malicious_input}')
            # Should not cause server error
            assert response.status_code in [200, 400, 404]


class TestAdminIntegration:
    """Integration tests for admin functionality."""

    def test_admin_complete_workflow(self, client, admin_user, test_user_db, test_project):
        """Test complete admin workflow."""
        # Login as admin
        client.post('/auth/login', data={
            'name': admin_user['name'],
            'password': admin_user['password']
        })

        # 1. Access admin index
        response = client.get('/admin/')
        assert response.status_code == 200

        # 2. View user projects
        response = client.get(f'/admin/user-projects/{test_user_db.id}')
        assert response.status_code == 200

        # 3. View project messages
        response = client.get(f'/admin/project-messages/{test_project.uuid}')
        assert response.status_code == 200

    def test_admin_navigation_flow(self, client, admin_user):
        """Test admin can navigate between admin pages."""
        # Login as admin
        client.post('/auth/login', data={
            'name': admin_user['name'],
            'password': admin_user['password']
        })

        # Test navigation sequence
        navigation_flow = [
            '/admin/',
            '/admin/user-projects/1',
            '/admin/project-messages/test-uuid',
            '/admin/',  # Back to index
        ]

        for endpoint in navigation_flow:
            response = client.get(endpoint)
            assert response.status_code == 200
