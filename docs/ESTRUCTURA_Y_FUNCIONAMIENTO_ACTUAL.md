# Estructura y funcionamiento actual (portfolio-ready)

Resumen de la arquitectura y los cambios aplicados para dejar el proyecto listo como **proyecto portfolio para trabajo**: arquitectura limpia, seguridad, testing, migraciones, soft delete, auditoría y documentación.

---

## 1. Estructura del backend

```
src/
  app/
    __init__.py      # create_app(); sin db.create_all() — solo migraciones
    config.py        # Development / Testing / Production; Redis para rate limit
    routes.py        # Registro de blueprints + / y /health (healthcheck con DB)
    extensions.py    # jwt, limiter, login_manager, admin
    errors.py        # Manejo global de errores
    models.py        # Re-export de api.models
  api/
    routes.py        # Stock CRUD, tipos, movimientos, mantenimiento, DELETE (soft)
    auth.py          # register, login (access+refresh), refresh, logout, /me
    users.py         # Usuarios (admin: list/create; self: get/update/delete)
    models.py        # User, Stock (deleted_at), StockMovement, StockHistory, ...
    services/
      stock_service.py   # Lógica: crear stock, inventario, búsqueda, soft_delete_stock
      auth_service.py     # Registro y validación de usuarios
    repositories/
      stock_repository.py # Solo datos: get_by_barcode, get_by_id, search, soft_delete, ...
```

**Flujo de una petición:**  
Ruta → Servicio (validación + lógica) → Repositorio (queries) → Modelo. Las rutas no acceden directamente a `Model.query` para stock; usan `StockService` y este usa `StockRepository`.

---

## 2. Base de datos y migraciones

- **Tablas:** Solo con **Flask-Migrate / Alembic** (`flask db upgrade`). No se usa `db.create_all()` en el arranque de la app.
- **Desarrollo:** Ejecutar `flask db upgrade` antes del primer `python src/run.py`.
- **Docker:** El servicio `migrate` corre `flask db upgrade`; `db-init` solo crea el usuario admin si no existe.
- **Stock:** Campo `deleted_at` para soft delete. Todas las consultas de listado y búsqueda excluyen registros con `deleted_at` no nulo.
- **Auditoría:** Tabla `stock_history` (stock_id, changed_by, action, old_value, new_value, timestamp). Se registra create, update y soft_delete.

---

## 3. Seguridad

- **Contraseñas:** Hash con werkzeug (`generate_password_hash` / `check_password_hash`).
- **JWT:** Access token corto (15 min por defecto); refresh token en cookie HTTP-only (ruta `/api/auth/refresh`). El frontend envía el access en `Authorization: Bearer ...`.
- **Rate limiting:** Auth blueprint 5/min; API 100/h. En Docker el backend usa **Redis** (`RATELIMIT_STORAGE_URL=redis://redis:6379/0`).
- **CORS:** Configurado por entorno (`CORS_ORIGINS`). Credenciales permitidas para cookies.
- **Nginx:** Headers X-Frame-Options, X-Content-Type-Options, Referrer-Policy; HSTS comentado para activar con HTTPS.

---

## 4. Endpoints relevantes

| Método | Ruta | Descripción |
|--------|------|-------------|
| POST | /api/auth/register | Registro |
| POST | /api/auth/login | Login (access + refresh cookie) |
| POST | /api/auth/refresh | Nuevo access token (cookie) |
| POST | /api/auth/logout | Limpia cookie refresh |
| GET | /api/auth/me | Usuario actual (y renovación de access si cerca de expirar) |
| GET | /api/stock/inventory | Resumen y detalle (excluye soft-deleted) |
| POST | /api/stock | Crear ítem (y registro en stock_history) |
| GET | /api/stock/<barcode> | Por código de barras (404 si deleted) |
| GET | /api/stock/search | Búsqueda paginada con filtros |
| **DELETE** | **/api/stock/<id>** | **Soft delete** (deleted_at + stock_history) |
| POST | /api/stock/<id>/movement | Registrar movimiento |
| POST | /api/stock/<id>/maintenance | Registrar mantenimiento |

---

## 5. Frontend

- **React Router** en `App.js`: rutas `/`, `/consultar`, `/admin`, `/login`; `ProtectedRoute` y `requireAdmin` para `/admin`.
- **Cliente API** (`api/client.js`): `apiFetch(path, options)`. Si recibe **401**, llama a `POST /api/auth/refresh` (con cookies), guarda el nuevo `access_token` en `localStorage` y **reintenta la petición original** una vez.
- **AuthStore:** Token, username, user_type en `localStorage`; verificación periódica con `/api/auth/me`; eventos para actualizar la UI.
- **React Query** disponible en el proyecto para cache y peticiones.

---

## 6. Docker

- **Servicios:** nginx, postgres, **redis**, client (frontend), server (backend), migrate, db-init, elasticsearch.
- **Redis:** Nuevo servicio; el server lo usa para rate limiting en producción.
- **Orden:** postgres + redis + elasticsearch → migrate → db-init → server (y client/nginx).
- Variables en `docker-compose`; para producción copiar `.env.example` a `.env` y usar valores seguros.

---

## 7. Tests

- **test_stock.py:** Crear stock, obtener por barcode, búsqueda, paginación, **test_soft_delete_stock** (crear → GET 200 → DELETE → GET 404).
- **test_permissions.py:** Admin puede listar/crear usuarios; usuario normal 403; sin token 401.
- **test_auth.py / test_auth_errors.py / test_integration.py:** Login, errores de auth, integración.

Ejecutar (con dependencias instaladas, p. ej. en venv):

```bash
PYTHONPATH=src pytest tests/ -v --cov=src --cov-report=term-missing
```

---

## 8. Archivos nuevos o modificados (resumen)

| Archivo | Cambio |
|---------|--------|
| `src/api/repositories/__init__.py` | Nuevo: export StockRepository |
| `src/api/repositories/stock_repository.py` | Nuevo: capa de acceso a datos de stock |
| `src/api/services/stock_service.py` | Usa StockRepository; añadido soft_delete_stock |
| `src/api/routes.py` | GET/movement/maintenance usan repository; nuevo DELETE /api/stock/<id> |
| `src/app/__init__.py` | Eliminado db.create_all() en desarrollo |
| `docker-compose.yml` | Servicio redis; RATELIMIT_STORAGE_URL; server depends_on redis |
| `.env.example` | Nuevo: plantilla de variables de entorno |
| `nginx/nginx.conf` | Comentario HSTS para HTTPS |
| `README.md` | Diagrama de arquitectura, decisiones técnicas, seguridad, tests, instalación con migraciones |
| `FUNCIONAMIENTO.md` | Actualizado: capas, migraciones, Redis, soft delete, refresh, estructura de directorios |
| `frontend/src/api/client.js` | Flujo 401 → refresh → reintento de petición |
| `tests/test_stock.py` | Añadido test_soft_delete_stock |
| `scripts/init_db.py` | Comentario: tablas vía migrate, no create_all |

---

## 9. Cómo contarlo en entrevista

Puedes resumir el proyecto así:

*"Diseñé una aplicación full-stack de inventario con arquitectura en capas (rutas, servicios, repositorios), autenticación JWT con access token corto y refresh en cookie HTTP-only, control de roles, migraciones versionadas con Flask-Migrate, soft delete y auditoría en base de datos, rate limiting con Redis, y tests automatizados (login, stock, permisos, soft delete), todo dockerizado para un despliegue reproducible."*

Esto transmite criterio arquitectónico y buenas prácticas sin overengineering.
