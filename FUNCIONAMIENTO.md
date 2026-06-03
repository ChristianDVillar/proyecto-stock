# Funcionamiento del Proyecto Stock

> Para el estado **actual del código** (rutas, permisos, CI, backlog de mejoras), ver [ESTRUCTURA_Y_FUNCIONAMIENTO_ACTUAL.md](ESTRUCTURA_Y_FUNCIONAMIENTO_ACTUAL.md).

Este documento describe la estructura actual y el flujo del sistema: arranque, capas del backend, componentes, autenticación y uso de la API.

---

## 1. Visión general

Proyecto Stock es una aplicación de gestión de inventario con arquitectura en capas:

- **Backend (Flask)**: API REST con separación **Rutas → Servicios → Repositorios → Modelos**. Autenticación JWT (access + refresh en cookie), migraciones con Flask-Migrate, soft delete y auditoría en `stock_history`, control de roles (`user_type` + decorador `@role_required`) y operaciones críticas envueltas en transacciones. Persistencia en PostgreSQL (o SQLite en desarrollo).
- **Frontend (React)**: React Router, React Query, cliente API centralizado; sesión con access token (p. ej. en localStorage) y refresh vía cookie.
- **Docker**: Nginx como puerta de entrada; Postgres, Redis (rate limit), Elasticsearch (búsqueda avanzada). Servicios `migrate` y `db-init` para esquema y usuario admin.

---

## 2. Cómo se arranca el sistema

### Con Docker

1. En la raíz: `docker-compose up -d`.
2. **Orden de arranque**:
   - **PostgreSQL**, **Redis** y **Elasticsearch** arrancan (con healthchecks).
   - **migrate**: ejecuta `flask db upgrade` (aplica migraciones).
   - **db-init**: script que crea usuario admin si no existe (no crea tablas; las migraciones ya las crearon).
   - **server** (backend) arranca cuando Postgres y Redis están ok y db-init ha terminado. Usa Redis para rate limiting (`RATELIMIT_STORAGE_URL`).
   - **client** (frontend) y **nginx** dependen de server/client.

3. **Puertos**: Nginx `9001` (todo junto); frontend directo `7000`; backend directo `3000`.

### Sin Docker (desarrollo)

1. **Backend**: Las tablas se crean **solo con migraciones** (no hay `db.create_all()` en `create_app()` salvo en entorno de tests).
   - Primera vez: `pip install -r requirements-dev.txt` (o `requirements.txt` si usas PostgreSQL), luego `PYTHONPATH=src`, `FLASK_APP=src/run.py`, `python -m flask db upgrade`, y `python src/run.py`. En Windows usa `python -m flask` para no depender del PATH.
   - El usuario admin inicial se crea con el script `scripts/init_db.py` (el mismo que usa el servicio `db-init` en Docker).
2. **Frontend**: `cd frontend`, `npm install`, `npm start` (proxy al backend en dev).

---

## 3. Componentes del sistema

| Componente | Función |
|------------|--------|
| **Nginx** | Sirve el frontend en `/` y reenvía `/api`, `/api-docs`, `/admin` al backend; headers de seguridad. |
| **client** | Build estático de React. |
| **server** | Flask (Gunicorn en prod); rate limit con Redis. |
| **postgres** | Base de datos principal. |
| **redis** | Backend de rate limiting (auth 5/min, API 100/h). |
| **migrate** | Ejecuta `flask db upgrade` una vez. |
| **db-init** | Crea usuario admin inicial si no existe. |
| **elasticsearch** | Búsqueda (opcional). |

---

## 4. Flujo del backend

1. **Entrada**: `src/run.py` → `create_app(env)` → servidor (o Gunicorn con `src/wsgi.py`).

2. **create_app** (`src/app/__init__.py`):
   - Configuración por entorno; extensiones: BD, CORS, JWT, Limiter, Flask-Login/Flask-Admin (para panel HTML legado), Swagger.
   - Blueprints: `api` (`/api`), `auth` (`/api/auth`), `users` (`/api/users`). Rate limit: auth 5/min, api 100/h.
   - **No** se ejecuta `db.create_all()` (salvo en entorno `testing`); las tablas se crean con `flask db upgrade`. El admin inicial se crea vía script `init_db.py` (servicio `db-init`).

3. **Estructura en capas**:
   - **Rutas** (`api/routes.py`, `api/auth.py`, `api/users.py`, `api/solicitudes.py`): reciben request, llaman a **servicios**, devuelven JSON.
   - **Servicios** (`api/services/stock_service.py`, `auth_service.py`): lógica de negocio, validaciones, transacciones; usan **repositorios** para leer/escribir.
   - **Repositorios** (`api/repositories/stock_repository.py`): solo consultas y persistencia (queries, filtros por `deleted_at`, etc.).
   - **Modelos** (`api/models.py`): User (con `user_type` para roles), Stock (con `deleted_at` para soft delete), StockMovement, MaintenanceRecord, StockHistory (auditoría), ItemRequest (solicitudes de elementos).

4. **Auth**:
   - Login devuelve **access token** (JSON + header `Authorization`) y **refresh token** (solo en cookie HTTP-only).
   - El frontend envía el access en `Authorization: Bearer ...`. Si el access expira, el cliente puede llamar a `POST /api/auth/refresh` (con cookie) para obtener un nuevo access.
   - Los endpoints sensibles usan `@jwt_required()` y, para rutas admin, un decorador de roles `@role_required('admin')` que valida `User.user_type` en el backend (RBAC simple pero explícito).

5. **Stock**:
   - Creación y búsqueda pasan por `StockService` y `StockRepository`.
   - Operaciones críticas (alta de stock + movimiento inicial + auditoría, soft delete + historial) se confirman con `db.session.commit()` en la ruta tras el servicio.
   - Eliminación: `DELETE /api/stock/<id>` hace **soft delete** (marca `deleted_at` y registra en `stock_history`). Las consultas excluyen siempre los registros con `deleted_at` no nulo.

---

## 5. Flujo del frontend

1. **Entrada**: `frontend/src/App.js` con **React Router** (`BrowserRouter`, `Routes`, `Route`). Al cargar se restaura sesión desde `localStorage` (`AuthStore`), se valida el token y se comprueba periódicamente con la API.

2. **Rutas** (en `App.js`):
   - `/` → NewInventory (protegida con `ProtectedRoute`).
   - `/consultar` → ConsultInventory (protegida).
   - `/admin` → UserDashboard (protegida y `requireAdmin`).
   - `/login` → Login (pública; si ya hay sesión redirige a `/`).
   - Cualquier otra ruta → redirección a `/`.

3. **API**: Cliente en `frontend/src/api/client.js` (`apiFetch`): base URL por `REACT_APP_API_URL` o proxy, token en `Authorization: Bearer ...`, `credentials: 'include'` para cookies (refresh). Opcional: en 401 intentar refresh y reintentar la petición.

4. **Estado**: `AuthStore` (token, username, user_type en localStorage; EventEmitter para notificar cambios). React Query para cache y peticiones a la API donde se use.

5. **Vistas**: Login → POST `/api/auth/login`; NewInventory y ConsultInventory → endpoints `/api/stock*`; UserDashboard → `/api/users` (solo admin).

---

## 6. Flujos de usuario típicos

- **Login**: `/login` → POST `/api/auth/login` → backend devuelve access token (JSON + cookie) y refresh token (cookie); frontend guarda access y datos de usuario, redirige a `/`.
- **Refresh**: Si el access expira, el frontend puede llamar POST `/api/auth/refresh` (con cookie) y obtener un nuevo access sin pedir de nuevo usuario/contraseña.
- **Crear stock**: Nuevo inventario → POST `/api/stock` con token → servicio valida, repositorio persiste, se registra en `stock_history`.
- **Consultar / Buscar**: GET `/api/stock/search` o `/api/stock/inventory` con token; resultados excluyen soft-deleted.
- **Eliminar (soft)**: DELETE `/api/stock/<id>` → se marca `deleted_at` y se registra en `stock_history`; el ítem deja de aparecer en listados y búsquedas.
- **Admin**: `/admin` → UserDashboard; endpoints `/api/users` con el mismo JWT (rol admin requerido).
- **Solicitar elementos (usuario)**:
  - Vista `SolicitarElementos` permite crear solicitudes de préstamo/uso.
  - Formulario: fecha de solicitud, tipo de duración (`semanas`, `horas` o `definitivo`), valor de duración (si aplica), casilla de firma y **selector opcional de elemento** (`stock_id`) cargado desde `GET /api/stock/search?per_page=200`.
  - Al enviar, hace `POST /api/solicitudes` con el JWT del usuario. Sus propias solicitudes se listan en la tabla \"Mis solicitudes\" con estado y fecha de entrega (si la define el admin).
- **Solicitar elementos (admin)**:
  - El mismo componente muestra para administradores la lista completa de solicitudes (`GET /api/solicitudes`) con columnas: usuario, elemento, fecha solicitud, tiempo, firmada, estado, fecha de entrega y acciones.
  - Desde esa tabla el admin puede **aprobar** o **rechazar** una solicitud pendiente mediante `PATCH /api/solicitudes/<id>` enviando `status` (`aprobado` / `rechazado`) y opcionalmente `delivery_date` (fecha de entrega).

---

## 7. Uso de la API desde fuera del frontend

- **Base**: Con Docker/Nginx: `http://localhost:9001/api`; directo al backend: `http://localhost:3000/api` (o el puerto configurado).
- **Autenticación**: POST `/api/auth/login` con `{"username":"...","password":"..."}`. Respuesta: `access_token` (usar en `Authorization: Bearer <token>`); refresh en cookie para `/api/auth/refresh`.
- **Endpoints típicos**:
  - `GET /api/stock/inventory` – inventario (excluye soft-deleted).
  - `POST /api/stock` – crear ítem.
  - `GET /api/stock/<barcode>` – por código de barras (404 si está soft-deleted).
  - `GET /api/stock/search?q=...&page=...` – búsqueda paginada.
  - `GET /api/stock/search_es?q=...` – búsqueda avanzada en Elasticsearch (full-text sobre barcode, inventario, modelo, descripción).
  - `DELETE /api/stock/<id>` – soft delete (marca `deleted_at`, registra en historial).
  - `POST /api/stock/<id>/movement` y `POST /api/stock/<id>/maintenance` – movimientos y mantenimientos.
  - `GET /api/solicitudes` – lista solicitudes del usuario autenticado; si el usuario es admin devuelve todas.
  - `POST /api/solicitudes` – crea una solicitud de elementos (`request_date`, `duration_type`, `duration_value` opcional, `signed`, `stock_id` opcional).
  - `PATCH /api/solicitudes/<id>` – **solo admin**; actualiza `status` (`pendiente`, `aprobado`, `rechazado`) y/o `delivery_date`.

Documentación interactiva: `/api-docs` (Swagger).

---

## 8. Inicialización de datos

- **Tablas**: Solo mediante **migraciones** (`flask db upgrade`). En Docker lo hace el servicio **migrate**; en desarrollo hay que ejecutarlo antes del primer `python src/run.py`.
- **Usuario admin**: Lo crea `init_default_admin()` al arrancar la app (si no existe). En Docker, **db-init** ejecuta un script que también puede crear el admin. Variables: `ADMIN_USERNAME`, `ADMIN_PASSWORD` (en producción usar `.env` seguro).

---

## 9. Estructura de directorios (backend)

```
src/
  app/           # Factory create_app, config, extensions, routes, errors
  api/
    routes.py    # Rutas stock, tipos, movimientos, mantenimiento, DELETE soft
    auth.py      # login, refresh, logout, register, /me
    users.py     # CRUD usuarios (admin)
    models.py    # User, Stock, StockMovement, MaintenanceRecord, StockHistory, ...
    services/    # Lógica de negocio: stock_service, auth_service
    repositories/ # Acceso a datos: stock_repository
migrations/      # Flask-Migrate / Alembic
tests/          # pytest: auth, stock, permissions, soft delete, integration
```

## 10. Resumen rápido

| Objetivo | Cómo |
|----------|------|
| Arrancar todo | `docker-compose up -d` o backend (tras `flask db upgrade`) + frontend. |
| Crear tablas | Solo migraciones: `flask db upgrade` (Docker: servicio migrate). |
| Admin inicial | `init_default_admin()` al arrancar o script db-init. |
| Login | POST `/api/auth/login` → access token + refresh en cookie. |
| Refresh token | POST `/api/auth/refresh` con cookie. |
| Stock (crear, buscar, soft delete) | Rutas `/api/stock*` con Bearer token. |
| Documentación API | `http://localhost:9001/api-docs`. |
