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
    
    with app.test_client() as client:
        with app.app_context():
            db.create_all()
            # Create test admin user
            admin_user = User(
                username='testadmin',
                password=generate_password_hash('testpass123'),
                user_type=UserTypeEnum.admin,
                is_active=True
            )
            db.session.add(admin_user)
            db.session.commit()
        yield client
        with app.app_context():
            db.drop_all()

def test_register_user(client):
    """Test user registration"""
    response = client.post('/api/auth/register', 
                         json={'username': 'testuser', 'password': 'testpass123'},
                         content_type='application/json')
    assert response.status_code == 201
    data = json.loads(response.data)
    assert 'user' in data
    assert data['user']['username'] == 'testuser'

def test_login_success(client):
    """Test successful login"""
    response = client.post('/api/auth/login',
                         json={'username': 'testadmin', 'password': 'testpass123'},
                         content_type='application/json')
    assert response.status_code == 200
    data = json.loads(response.data)
    assert 'access_token' in data
    assert 'user' in data

def test_login_failure(client):
    """Test login with wrong credentials"""
    response = client.post('/api/auth/login',
                         json={'username': 'testadmin', 'password': 'wrongpass'},
                         content_type='application/json')
    assert response.status_code == 401

def test_get_current_user(client):
    """Test getting current user info"""
    # First login
    login_response = client.post('/api/auth/login',
                                json={'username': 'testadmin', 'password': 'testpass123'},
                                content_type='application/json')
    login_data = json.loads(login_response.data)
    token = login_data['access_token']
    
    # Get current user
    response = client.get('/api/auth/me',
                         headers={'Authorization': f'Bearer {token}'})
    assert response.status_code == 200
    data = json.loads(response.data)
    assert 'username' in data
    assert data['username'] == 'testadmin'

