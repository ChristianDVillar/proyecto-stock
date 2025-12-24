# Arquitectura del Sistema

## Diagrama de Arquitectura

```
┌─────────────────────────────────────────────────────────────┐
│                        CLIENT LAYER                         │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐     │
│  │   Web App    │  │  Mobile App  │  │  Admin Panel │     │
│  │   (React)    │  │ (React Native)│ │  (Flask-Admin)│     │
│  └──────┬───────┘  └──────┬───────┘  └──────┬───────┘     │
│         │                 │                  │              │
└─────────┼─────────────────┼──────────────────┼──────────────┘
          │                 │                  │
          │  HTTP/REST      │  HTTP/REST       │
          │  JWT Auth       │  JWT Auth        │
          │                 │                  │
┌─────────┼─────────────────┼──────────────────┼──────────────┐
│         │                 │                  │              │
│  ┌──────▼─────────────────▼──────────────────▼──────┐    │
│  │           API GATEWAY / BACKEND (Flask)            │    │
│  ├────────────────────────────────────────────────────┤    │
│  │                                                     │    │
│  │  ┌────────────┐  ┌────────────┐  ┌────────────┐  │    │
│  │  │   Auth     │  │   Stock    │  │   Users    │  │    │
│  │  │  Routes    │  │   Routes   │  │   Routes   │  │    │
│  │  └─────┬──────┘  └─────┬──────┘  └─────┬──────┘  │    │
│  │        │               │                │          │    │
│  │  ┌─────▼───────────────▼────────────────▼──────┐ │    │
│  │  │           Business Logic Services             │ │    │
│  │  │  - StockService                               │ │    │
│  │  │  - AuthService                                │ │    │
│  │  └─────┬──────────────────────────────────────┬──┘ │    │
│  │        │                                      │     │    │
│  │  ┌─────▼──────────┐              ┌──────────▼───┐ │    │
│  │  │  Validators    │              │   Utils      │ │    │
│  │  │  - Barcode     │              │   - Logger   │ │    │
│  │  │  - Username    │              │   - Errors   │ │    │
│  │  └───────────────┘              └──────────────┘ │    │
│  │                                                   │    │
│  └───────────────────────┬──────────────────────────┘    │
│                          │                                 │
└──────────────────────────┼─────────────────────────────────┘
                           │
                           │ SQLAlchemy ORM
                           │
┌──────────────────────────▼─────────────────────────────────┐
│                    DATA LAYER                               │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  ┌────────────────────────────────────────────────────┐   │
│  │              DATABASE (SQLite/PostgreSQL)          │   │
│  │                                                     │   │
│  │  ┌──────────┐  ┌──────────┐  ┌──────────┐        │   │
│  │  │  Users   │  │  Stock    │  │ Movements│        │   │
│  │  │  Forms   │  │  Types    │  │ Maintenance│      │   │
│  │  └──────────┘  └──────────┘  └──────────┘        │   │
│  │                                                     │   │
│  └────────────────────────────────────────────────────┘   │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

## Flujo de Datos

### 1. Autenticación
```
Usuario → Login Form → POST /api/auth/login
                      ↓
                  Auth Route → Validar credenciales
                      ↓
                  Generar JWT → Retornar token
                      ↓
                  Frontend almacena token en localStorage
```

### 2. Crear Stock
```
Usuario → NewInventory Form → Escanear código
                              ↓
                          POST /api/stock (con JWT)
                              ↓
                          Stock Route → Validar JWT
                              ↓
                          StockService → Validar datos
                              ↓
                          Crear registro en DB
                              ↓
                          Retornar éxito/error
```

### 3. Buscar Stock
```
Usuario → ConsultInventory → GET /api/stock/search?q=query
                              ↓
                          Stock Route → Validar JWT
                              ↓
                          StockService → Aplicar filtros
                              ↓
                          Query DB con paginación
                              ↓
                          Retornar resultados
```

## Componentes Principales

### Backend

1. **Application Factory** (`app/__init__.py`)
   - Crea y configura la aplicación Flask
   - Inicializa extensiones
   - Registra blueprints

2. **Configuration** (`app/config.py`)
   - Configuración por entornos (dev/test/prod)
   - Variables de entorno
   - Seguridad

3. **Routes** (`api/routes.py`, `api/auth.py`, `api/users.py`)
   - Endpoints REST
   - Validación de entrada
   - Rate limiting

4. **Services** (`app/services/`)
   - Lógica de negocio
   - Separación de responsabilidades
   - Reutilizable

5. **Models** (`api/models.py`)
   - Definición de esquema de BD
   - Relaciones
   - Validaciones a nivel de modelo

### Frontend

1. **Components** (`js/components/`)
   - Componentes React reutilizables
   - Separación por funcionalidad

2. **Stores** (`stores/`)
   - Patrón Flux
   - Estado global
   - EventEmitter

3. **Actions** (`actions/`)
   - Acciones del patrón Flux
   - Comunicación con API

## Seguridad

- **JWT Authentication**: Tokens con expiración
- **Rate Limiting**: Protección contra abuso
- **CORS**: Configuración restrictiva
- **Input Validation**: Validación en frontend y backend
- **SQL Injection Protection**: SQLAlchemy ORM
- **Error Handling**: No exposición de información sensible

## Escalabilidad

- **Stateless API**: Fácil escalado horizontal
- **Database Pooling**: Conexiones eficientes
- **Caching Ready**: Preparado para Redis
- **Microservices Ready**: Estructura modular

