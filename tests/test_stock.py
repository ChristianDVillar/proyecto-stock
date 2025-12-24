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

@pytest.fixture
def auth_token(client):
    """Get authentication token"""
    response = client.post('/api/auth/login',
                         json={'username': 'testuser', 'password': 'testpass123'},
                         content_type='application/json')
    data = json.loads(response.data)
    return data['access_token']

def test_create_stock(client, auth_token):
    """Test creating a new stock item"""
    stock_data = {
        'barcode': 'TEST123',
        'inventario': 'INV001',
        'dispositivo': 'computadora',
        'modelo': 'Test Model',
        'cantidad': 5
    }
    
    response = client.post('/api/stock',
                          json=stock_data,
                          headers={'Authorization': f'Bearer {auth_token}'},
                          content_type='application/json')
    
    assert response.status_code == 201
    data = json.loads(response.data)
    assert 'id' in data
    assert data['barcode'] == 'TEST123'

def test_get_stock(client, auth_token):
    """Test getting stock by barcode"""
    # First create a stock
    stock_data = {
        'barcode': 'TEST456',
        'inventario': 'INV002',
        'dispositivo': 'laptop',
        'modelo': 'Test Laptop',
        'cantidad': 3
    }
    client.post('/api/stock',
               json=stock_data,
               headers={'Authorization': f'Bearer {auth_token}'},
               content_type='application/json')
    
    # Then get it
    response = client.get('/api/stock/TEST456',
                         headers={'Authorization': f'Bearer {auth_token}'})
    
    assert response.status_code == 200
    data = json.loads(response.data)
    assert data['stock']['barcode'] == 'TEST456'

def test_search_stock(client, auth_token):
    """Test searching stock"""
    # Create test stocks
    stocks = [
        {
            'barcode': 'SEARCH001',
            'inventario': 'INV003',
            'dispositivo': 'monitor',
            'modelo': 'Monitor Test',
            'cantidad': 2
        },
        {
            'barcode': 'SEARCH002',
            'inventario': 'INV004',
            'dispositivo': 'teclado',
            'modelo': 'Keyboard Test',
            'cantidad': 10
        }
    ]
    
    for stock in stocks:
        client.post('/api/stock',
                   json=stock,
                   headers={'Authorization': f'Bearer {auth_token}'},
                   content_type='application/json')
    
    # Search
    response = client.get('/api/stock/search?q=Monitor',
                         headers={'Authorization': f'Bearer {auth_token}'})
    
    assert response.status_code == 200
    data = json.loads(response.data)
    assert len(data['stocks']) > 0
    assert any(s['barcode'] == 'SEARCH001' for s in data['stocks'])

def test_search_stock_pagination(client, auth_token):
    """Test stock search with pagination"""
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
                   headers={'Authorization': f'Bearer {auth_token}'},
                   content_type='application/json')
    
    # Test pagination
    response = client.get('/api/stock/search?page=1&per_page=10',
                         headers={'Authorization': f'Bearer {auth_token}'})
    
    assert response.status_code == 200
    data = json.loads(response.data)
    assert 'total_pages' in data
    assert 'total_items' in data
    assert len(data['stocks']) <= 10

