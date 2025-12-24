"""
Tests for stock operations error handling
"""
import pytest
import json
from src.app import create_app
from src.app.models import db, User, Stock, StockTypeEnum, StockStatusEnum, UserTypeEnum
from werkzeug.security import generate_password_hash


@pytest.fixture
def client():
    """Create a test client"""
    app = create_app('testing')
    
    with app.test_client() as client:
        with app.app_context():
            db.create_all()
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


@pytest.fixture
def auth_token(client):
    """Get authentication token"""
    response = client.post('/api/auth/login',
                         json={'username': 'testuser', 'password': 'testpass123'},
                         content_type='application/json')
    data = json.loads(response.data)
    return data['access_token']


def test_create_stock_with_missing_fields(client, auth_token):
    """Test creating stock with missing required fields"""
    # Missing barcode
    response = client.post('/api/stock',
                          json={
                              'inventario': 'INV001',
                              'dispositivo': 'laptop',
                              'modelo': 'Test Model'
                          },
                          headers={'Authorization': f'Bearer {auth_token}'},
                          content_type='application/json')
    assert response.status_code == 400
    data = json.loads(response.data)
    assert 'error' in data


def test_create_stock_with_duplicate_barcode(client, auth_token):
    """Test creating stock with duplicate barcode"""
    # Create first stock
    stock_data = {
        'barcode': 'DUPLICATE001',
        'inventario': 'INV001',
        'dispositivo': 'laptop',
        'modelo': 'Test Model',
        'cantidad': 1
    }
    client.post('/api/stock',
               json=stock_data,
               headers={'Authorization': f'Bearer {auth_token}'},
               content_type='application/json')
    
    # Try to create duplicate
    response = client.post('/api/stock',
                          json=stock_data,
                          headers={'Authorization': f'Bearer {auth_token}'},
                          content_type='application/json')
    assert response.status_code == 400
    data = json.loads(response.data)
    assert 'duplicado' in data['error'].lower() or 'duplicate' in data['error'].lower()


def test_create_stock_with_invalid_cantidad(client, auth_token):
    """Test creating stock with invalid cantidad"""
    stock_data = {
        'barcode': 'INVALID001',
        'inventario': 'INV001',
        'dispositivo': 'laptop',
        'modelo': 'Test Model',
        'cantidad': -5  # Invalid negative
    }
    
    response = client.post('/api/stock',
                          json=stock_data,
                          headers={'Authorization': f'Bearer {auth_token}'},
                          content_type='application/json')
    assert response.status_code == 400


def test_create_stock_with_invalid_device_type(client, auth_token):
    """Test creating stock with invalid device type"""
    stock_data = {
        'barcode': 'INVALID002',
        'inventario': 'INV001',
        'dispositivo': 'invalid_device_type',
        'modelo': 'Test Model',
        'cantidad': 1
    }
    
    response = client.post('/api/stock',
                          json=stock_data,
                          headers={'Authorization': f'Bearer {auth_token}'},
                          content_type='application/json')
    assert response.status_code == 400


def test_get_stock_with_nonexistent_barcode(client, auth_token):
    """Test getting stock that doesn't exist"""
    response = client.get('/api/stock/NONEXISTENT123',
                         headers={'Authorization': f'Bearer {auth_token}'})
    assert response.status_code == 404


def test_search_stock_with_invalid_pagination(client, auth_token):
    """Test search with invalid pagination parameters"""
    # Invalid page number
    response = client.get('/api/stock/search?page=0',
                         headers={'Authorization': f'Bearer {auth_token}'})
    # Should handle gracefully (either 400 or default to page 1)
    assert response.status_code in [200, 400]
    
    # Invalid per_page (too large)
    response = client.get('/api/stock/search?per_page=1000',
                         headers={'Authorization': f'Bearer {auth_token}'})
    # Should cap at 100
    if response.status_code == 200:
        data = json.loads(response.data)
        assert data.get('per_page', 100) <= 100

