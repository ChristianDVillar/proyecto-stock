"""
Integration tests for the API
"""
import pytest
import json
from src.app import app
from src.api.models import db, User, Stock, StockTypeEnum, StockStatusEnum, UserTypeEnum
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
            # Create test users
            admin = User(
                username='admin',
                password=generate_password_hash('admin123'),
                user_type=UserTypeEnum.admin,
                is_active=True
            )
            user = User(
                username='user',
                password=generate_password_hash('user123'),
                user_type=UserTypeEnum.user,
                is_active=True
            )
            db.session.add(admin)
            db.session.add(user)
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
    """Get user authentication token"""
    response = client.post('/api/auth/login',
                         json={'username': 'user', 'password': 'user123'},
                         content_type='application/json')
    data = json.loads(response.data)
    return data['access_token']

def test_full_workflow(client, admin_token):
    """Test complete workflow: create stock, search, view details"""
    # Create stock
    stock_data = {
        'barcode': 'WORKFLOW001',
        'inventario': 'INV001',
        'dispositivo': 'computadora',
        'modelo': 'Test Model',
        'cantidad': 10
    }
    
    create_response = client.post('/api/stock',
                                 json=stock_data,
                                 headers={'Authorization': f'Bearer {admin_token}'},
                                 content_type='application/json')
    assert create_response.status_code == 201
    
    # Search for the stock
    search_response = client.get('/api/stock/search?q=WORKFLOW001',
                                headers={'Authorization': f'Bearer {admin_token}'})
    assert search_response.status_code == 200
    search_data = json.loads(search_response.data)
    assert len(search_data['stocks']) > 0
    assert search_data['stocks'][0]['barcode'] == 'WORKFLOW001'
    
    # Get stock details
    details_response = client.get('/api/stock/WORKFLOW001',
                                 headers={'Authorization': f'Bearer {admin_token}'})
    assert details_response.status_code == 200
    details_data = json.loads(details_response.data)
    assert details_data['stock']['barcode'] == 'WORKFLOW001'

def test_user_permissions(client, user_token, admin_token):
    """Test that regular users cannot access admin endpoints"""
    # Regular user cannot get all users
    response = client.get('/api/users',
                         headers={'Authorization': f'Bearer {user_token}'})
    assert response.status_code == 403
    
    # Admin can get all users
    response = client.get('/api/users',
                         headers={'Authorization': f'Bearer {admin_token}'})
    assert response.status_code == 200

def test_pagination(client, admin_token):
    """Test pagination functionality"""
    # Create multiple stocks
    for i in range(25):
        stock_data = {
            'barcode': f'PAGE{i:03d}',
            'inventario': f'INV{i:03d}',
            'dispositivo': 'computadora',
            'modelo': f'Model {i}',
            'cantidad': 1
        }
        client.post('/api/stock',
                   json=stock_data,
                   headers={'Authorization': f'Bearer {admin_token}'},
                   content_type='application/json')
    
    # Test first page
    response = client.get('/api/stock/search?page=1&per_page=10',
                         headers={'Authorization': f'Bearer {admin_token}'})
    assert response.status_code == 200
    data = json.loads(response.data)
    assert len(data['stocks']) == 10
    assert data['current_page'] == 1
    assert data['total_pages'] == 3
    
    # Test second page
    response = client.get('/api/stock/search?page=2&per_page=10',
                         headers={'Authorization': f'Bearer {admin_token}'})
    assert response.status_code == 200
    data = json.loads(response.data)
    assert len(data['stocks']) == 10
    assert data['current_page'] == 2

