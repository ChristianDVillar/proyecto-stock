"""
Tests for permissions and authorization
"""
import pytest
import json
from src.app import app
from src.api.models import db, User, UserTypeEnum
from werkzeug.security import generate_password_hash

@pytest.fixture
def client():
    """Create a test client"""
    app.config['TESTING'] = True
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
    app.config['JWT_SECRET_KEY'] = 'test-secret-key'
    app.config['SECRET_KEY'] = 'test-secret-key'
    app.config['RATELIMIT_ENABLED'] = False
    
    with app.test_client() as client:
        with app.app_context():
            db.create_all()
            # Create test users
            admin = User(
                username='admin',
                password=generate_password_hash('admin123'),
                user_type=UserTypeEnum.admin,
                is_active=True
            )
            regular_user = User(
                username='user',
                password=generate_password_hash('user123'),
                user_type=UserTypeEnum.user,
                is_active=True
            )
            db.session.add(admin)
            db.session.add(regular_user)
            db.session.commit()
        yield client
        with app.app_context():
            db.drop_all()

@pytest.fixture
def admin_token(client):
    """Get admin authentication token"""
    response = client.post('/api/auth/login',
                         json={'username': 'admin', 'password': 'admin123'},
                         content_type='application/json')
    data = json.loads(response.data)
    return data['access_token']

@pytest.fixture
def user_token(client):
    """Get regular user authentication token"""
    response = client.post('/api/auth/login',
                         json={'username': 'user', 'password': 'user123'},
                         content_type='application/json')
    data = json.loads(response.data)
    return data['access_token']

def test_admin_can_get_all_users(client, admin_token):
    """Test that admin can get all users"""
    response = client.get('/api/users',
                         headers={'Authorization': f'Bearer {admin_token}'})
    assert response.status_code == 200
    data = json.loads(response.data)
    assert 'users' in data
    assert len(data['users']) >= 2

def test_regular_user_cannot_get_all_users(client, user_token):
    """Test that regular user cannot get all users"""
    response = client.get('/api/users',
                         headers={'Authorization': f'Bearer {user_token}'})
    assert response.status_code == 403

def test_regular_user_cannot_create_user(client, user_token):
    """Test that regular user cannot create users"""
    response = client.post('/api/users',
                          json={'username': 'newuser', 'password': 'pass123'},
                          headers={'Authorization': f'Bearer {user_token}'},
                          content_type='application/json')
    assert response.status_code == 403

def test_admin_can_create_user(client, admin_token):
    """Test that admin can create users"""
    response = client.post('/api/users',
                          json={'username': 'newuser', 'password': 'pass123', 'user_type': 'user'},
                          headers={'Authorization': f'Bearer {admin_token}'},
                          content_type='application/json')
    assert response.status_code == 201

def test_unauthenticated_cannot_access_protected_endpoint(client):
    """Test that unauthenticated requests are rejected"""
    response = client.get('/api/users')
    assert response.status_code == 401

def test_invalid_token_is_rejected(client):
    """Test that invalid tokens are rejected"""
    response = client.get('/api/users',
                         headers={'Authorization': 'Bearer invalid-token'})
    assert response.status_code == 401

