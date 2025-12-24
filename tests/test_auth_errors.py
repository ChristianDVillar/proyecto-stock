"""
Tests for authentication error handling and edge cases
"""
import pytest
import json
from src.app import create_app
from src.app.models import db, User, UserTypeEnum
from werkzeug.security import generate_password_hash


@pytest.fixture
def client():
    """Create a test client"""
    app = create_app('testing')
    
    with app.test_client() as client:
        with app.app_context():
            db.create_all()
            # Create test user
            test_user = User(
                username='testuser',
                password=generate_password_hash('testpass123'),
                user_type=UserTypeEnum.user,
                is_active=True
            )
            db.session.add(test_user)
            db.session.commit()
        yield client
        with app.app_context():
            db.drop_all()


def test_login_with_invalid_credentials(client):
    """Test login with wrong password"""
    response = client.post('/api/auth/login',
                         json={'username': 'testuser', 'password': 'wrongpassword'},
                         content_type='application/json')
    assert response.status_code == 401
    data = json.loads(response.data)
    assert 'error' in data


def test_login_with_nonexistent_user(client):
    """Test login with user that doesn't exist"""
    response = client.post('/api/auth/login',
                         json={'username': 'nonexistent', 'password': 'password'},
                         content_type='application/json')
    assert response.status_code == 401


def test_login_with_missing_fields(client):
    """Test login with missing username or password"""
    # Missing password
    response = client.post('/api/auth/login',
                         json={'username': 'testuser'},
                         content_type='application/json')
    assert response.status_code == 400
    
    # Missing username
    response = client.post('/api/auth/login',
                         json={'password': 'testpass123'},
                         content_type='application/json')
    assert response.status_code == 400


def test_register_with_existing_username(client):
    """Test registration with existing username"""
    response = client.post('/api/auth/register',
                         json={'username': 'testuser', 'password': 'newpass123'},
                         content_type='application/json')
    assert response.status_code == 400
    data = json.loads(response.data)
    assert 'error' in data


def test_register_with_invalid_username(client):
    """Test registration with invalid username format"""
    response = client.post('/api/auth/register',
                         json={'username': 'ab', 'password': 'password123'},
                         content_type='application/json')
    assert response.status_code == 400


def test_register_with_weak_password(client):
    """Test registration with password too short"""
    response = client.post('/api/auth/register',
                         json={'username': 'newuser', 'password': '12345'},
                         content_type='application/json')
    assert response.status_code == 400


def test_access_protected_endpoint_without_token(client):
    """Test accessing protected endpoint without token"""
    response = client.get('/api/stock/search')
    assert response.status_code == 401


def test_access_protected_endpoint_with_invalid_token(client):
    """Test accessing protected endpoint with invalid token"""
    response = client.get('/api/stock/search',
                         headers={'Authorization': 'Bearer invalid-token'})
    assert response.status_code == 401


def test_access_admin_endpoint_as_regular_user(client):
    """Test accessing admin endpoint as regular user"""
    # Login as regular user
    login_response = client.post('/api/auth/login',
                                json={'username': 'testuser', 'password': 'testpass123'},
                                content_type='application/json')
    login_data = json.loads(login_response.data)
    token = login_data['access_token']
    
    # Try to access admin endpoint
    response = client.get('/api/users',
                         headers={'Authorization': f'Bearer {token}'})
    assert response.status_code == 403

