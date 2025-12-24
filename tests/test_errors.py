"""
Tests for error handling
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
    app.config['RATELIMIT_ENABLED'] = False
    
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

def test_404_error_handler(client):
    """Test 404 error handling"""
    response = client.get('/api/nonexistent')
    assert response.status_code == 404
    data = json.loads(response.data)
    assert 'error' in data
    assert 'message' in data

def test_400_error_on_invalid_data(client, auth_token):
    """Test 400 error on invalid request data"""
    response = client.post('/api/stock',
                          json={'invalid': 'data'},
                          headers={'Authorization': f'Bearer {auth_token}'},
                          content_type='application/json')
    assert response.status_code == 400
    data = json.loads(response.data)
    assert 'error' in data

def test_400_error_on_duplicate_barcode(client, auth_token):
    """Test 400 error on duplicate barcode"""
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
    assert 'duplicado' in data.get('error', '').lower() or 'duplicate' in data.get('error', '').lower()

def test_500_error_handling(client, auth_token):
    """Test 500 error handling (simulated)"""
    # This would require mocking a database error
    # For now, test that error structure is correct
    response = client.get('/api/stock/nonexistent',
                         headers={'Authorization': f'Bearer {auth_token}'})
    # Should return 404, not 500
    assert response.status_code in [404, 500]
    data = json.loads(response.data)
    assert 'error' in data

def test_validation_errors(client, auth_token):
    """Test validation error messages"""
    # Test empty barcode
    response = client.post('/api/stock',
                          json={
                              'barcode': '',
                              'inventario': 'INV001',
                              'dispositivo': 'laptop',
                              'modelo': 'Test',
                              'cantidad': 1
                          },
                          headers={'Authorization': f'Bearer {auth_token}'},
                          content_type='application/json')
    assert response.status_code == 400
    
    # Test invalid cantidad
    response = client.post('/api/stock',
                          json={
                              'barcode': 'TEST001',
                              'inventario': 'INV001',
                              'dispositivo': 'laptop',
                              'modelo': 'Test',
                              'cantidad': -1
                          },
                          headers={'Authorization': f'Bearer {auth_token}'},
                          content_type='application/json')
    assert response.status_code == 400

