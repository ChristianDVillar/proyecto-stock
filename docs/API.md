# API Documentation

## Base URL
```
http://localhost:5000/api
```

## Authentication

All protected endpoints require a JWT token in the Authorization header:
```
Authorization: Bearer <token>
```

## Endpoints

### Authentication

#### POST /api/auth/register
Register a new user.

**Request Body:**
```json
{
  "username": "newuser",
  "password": "password123"
}
```

**Response (201):**
```json
{
  "message": "Usuario registrado exitosamente",
  "user": {
    "id": 1,
    "username": "newuser",
    "user_type": "user"
  }
}
```

#### POST /api/auth/login
Login and get JWT token.

**Request Body:**
```json
{
  "username": "admin",
  "password": "admin123"
}
```

**Response (200):**
```json
{
  "access_token": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "user": {
    "id": 1,
    "username": "admin",
    "user_type": "admin"
  }
}
```

#### GET /api/auth/me
Get current user information.

**Headers:**
```
Authorization: Bearer <token>
```

**Response (200):**
```json
{
  "username": "admin",
  "user_type": "admin",
  "is_active": true
}
```

### Stock Management

#### GET /api/stock/search
Search stock items with filters and pagination.

**Query Parameters:**
- `q` (string, optional): Search query
- `type` (string, optional): Filter by device type
- `status` (string, optional): Filter by status (disponible, en_uso, mantenimiento, baja)
- `location` (string, optional): Filter by location
- `page` (int, optional): Page number (default: 1)
- `per_page` (int, optional): Items per page (default: 20, max: 100)

**Example:**
```
GET /api/stock/search?q=laptop&status=disponible&page=1&per_page=20
```

**Response (200):**
```json
{
  "stocks": [
    {
      "id": 1,
      "barcode": "LAP001",
      "inventario": "INV001",
      "dispositivo": "laptop",
      "modelo": "Dell XPS 15",
      "cantidad": 5,
      "status": "disponible",
      "location": "Almacén A"
    }
  ],
  "total_items": 1,
  "total_pages": 1,
  "current_page": 1,
  "per_page": 20
}
```

#### POST /api/stock
Create a new stock item.

**Request Body:**
```json
{
  "barcode": "LAP001",
  "inventario": "INV001",
  "dispositivo": "laptop",
  "modelo": "Dell XPS 15",
  "descripcion": "Laptop Dell XPS 15",
  "cantidad": 5,
  "purchase_date": "2024-01-15",
  "warranty_expiry": "2025-01-15",
  "location": "Almacén A"
}
```

**Response (201):**
```json
{
  "message": "Stock creado exitosamente",
  "id": 1,
  "barcode": "LAP001"
}
```

#### GET /api/stock/<barcode>
Get stock details by barcode.

**Response (200):**
```json
{
  "stock": {
    "id": 1,
    "barcode": "LAP001",
    "inventario": "INV001",
    "dispositivo": "laptop",
    "modelo": "Dell XPS 15",
    "cantidad": 5,
    "status": "disponible",
    "location": "Almacén A"
  },
  "movements": [
    {
      "type": "entrada",
      "quantity": 5,
      "timestamp": "2024-01-15T10:00:00",
      "notes": "Registro inicial"
    }
  ],
  "last_maintenance": null
}
```

### User Management (Admin only)

#### GET /api/users
Get all users (Admin only).

**Response (200):**
```json
{
  "users": [
    {
      "id": 1,
      "username": "admin",
      "user_type": "admin",
      "is_active": true
    }
  ]
}
```

#### POST /api/users
Create a new user (Admin only).

**Request Body:**
```json
{
  "username": "newuser",
  "password": "password123",
  "user_type": "user",
  "is_active": true
}
```

## Error Responses

All errors follow this format:

```json
{
  "error": "Error description",
  "message": "Detailed error message"
}
```

**Status Codes:**
- `400`: Bad Request
- `401`: Unauthorized
- `403`: Forbidden
- `404`: Not Found
- `500`: Internal Server Error

## Swagger Documentation

Interactive API documentation is available at:
```
http://localhost:5000/api-docs
```

