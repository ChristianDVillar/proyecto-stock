# Estructura y funcionamiento actual

Documento de referencia del estado **real** del proyecto (código en rama `development`), pensado para planificar mejoras futuras. Complementa [FUNCIONAMIENTO.md](FUNCIONAMIENTO.md) con detalle técnico al día.

**Última revisión:** 2026

---

## 1. Visión general

| Capa | Tecnología | Rol |
|------|------------|-----|
| Frontend | React 18, React Router 6, TanStack React Query | SPA: inventario, consultas, solicitudes, admin |
| Backend | Flask 3, SQLAlchemy 2, Flask-JWT-Extended | API REST en capas |
| BD | PostgreSQL (prod/Docker) / SQLite (dev/tests) | Persistencia |
| Infra | Docker Compose, Nginx, Redis, Elasticsearch | Proxy, rate limit, búsqueda avanzada |
| CI | GitHub Actions (`.github/workflows/ci.yml`) | pytest + build frontend en `main` y `development` |

**Arquitectura backend:** Rutas → Servicios → Repositorios → Modelos.

---

## 2. Estructura de directorios

```
proyecto-stock/
├── frontend/                 # SPA React (servicio Docker: client)
│   └── src/
│       ├── App.js            # Router y layout
│       ├── api/client.js     # apiFetch + refresh automático
│       ├── stores/           # AuthStore, InventoryStore
│       ├── js/components/    # Vistas y ProtectedRoute
│       └── styles/
├── src/                      # Backend Python
│   ├── run.py                # Entrada desarrollo
│   ├── wsgi.py               # Entrada Gunicorn (prod)
│   ├── app/                  # Factory, config, health/ready
│   │   ├── __init__.py       # create_app()
│   │   ├── config.py         # development | testing | production
│   │   ├── routes.py         # Blueprints + /health + /ready
│   │   ├── models.py         # Re-export desde api.models
│   │   └── extensions.py     # jwt, limiter, admin, login
│   └── api/
│       ├── routes.py         # Stock, tipos, movimientos, mantenimiento
│       ├── auth.py           # login, refresh, logout, register, /me
│       ├── users.py          # CRUD usuarios (admin)
│       ├── solicitudes.py    # Solicitudes de elementos
│       ├── models.py         # Entidades SQLAlchemy
│       ├── utils.py          # Validaciones, @role_required, error_handler
│       ├── services/         # stock_service, auth_service
│       └── repositories/     # stock_repository
├── migrations/               # Flask-Migrate / Alembic
├── tests/                    # pytest (33 tests)
├── scripts/init_db.py        # Usuario admin (no crea tablas)
├── nginx/                    # Proxy reverso
├── docker-compose.yml
├── requirements.txt
├── pytest.ini                # pythonpath = src
├── README.md
├── FUNCIONAMIENTO.md
├── TECH_DECISIONS.md
└── SECURITY.md
```

> **Nota:** Existe una carpeta `src/` en la raíz con archivos React antiguos/duplicados. El frontend activo es **`frontend/`** (usado por Docker y CI).

---

## 3. Arranque del sistema

### Docker (`docker-compose up -d`)

1. **postgres**, **redis**, **elasticsearch** (healthchecks).
2. **migrate** → `flask db upgrade`.
3. **db-init** → `scripts/init_db.py` (admin si no existe).
4. **server** (Flask/Gunicorn) cuando postgres, redis y db-init están listos.
5. **client** (build React) y **nginx** (puerto **9001**).

| Servicio | Puerto | Función |
|----------|--------|---------|
| nginx | 9001 | Frontend + proxy `/api`, `/api-docs`, `/admin` |
| server | 3000 | API Flask directa |
| client | 7000 | Frontend directo (dev) |
| postgres | 5432 | BD |
| redis | 6379 | Rate limiting |
| elasticsearch | 9200 | Búsqueda full-text (`/api/stock/search_es`) |

### Desarrollo local

**Backend:**
```powershell
pip install -r requirements-dev.txt
$env:PYTHONPATH = "src"
$env:FLASK_APP = "src/run.py"
python -m flask db upgrade
python src/run.py
```

**Frontend:**
```bash
cd frontend && npm install && npm start
```

**Tests:**
```bash
python -m pytest tests/ -v --cov=src
```

Las tablas **no** se crean con `db.create_all()` en desarrollo/producción; solo en entorno `testing`. El admin inicial: `scripts/init_db.py` o servicio `db-init`.

---

## 4. Backend: capas y responsabilidades

### 4.1 Factory (`src/app/__init__.py`)

- Carga config por entorno (`development`, `testing`, `production`).
- Extensiones: SQLAlchemy, JWT, CORS, Limiter, Migrate, Swagger, Flask-Admin (no en testing).
- Blueprints registrados en `app/routes.py`.
- Rate limit: **auth** 5/min, **api** 100/h.
- En `testing`: `db.create_all()` para SQLite en memoria.

### 4.2 Rutas (blueprints)

| Prefijo | Archivo | Endpoints principales |
|---------|---------|------------------------|
| `/api` | `api/routes.py` | stock CRUD, búsqueda, tipos, movimientos, mantenimiento |
| `/api/auth` | `api/auth.py` | login, refresh, logout, register, `/me` |
| `/api/users` | `api/users.py` | CRUD usuarios (solo admin) |
| `/api/solicitudes` | `api/solicitudes.py` | listar, crear, PATCH admin |
| `/` | `app/routes.py` | ping JSON |
| `/health` | `app/routes.py` | DB ok → 200, fallo → 503 |
| `/ready` | `app/routes.py` | DB + Redis (si configurado) |

### 4.3 Servicios

- **`StockService`**: crear stock, búsqueda, inventario, soft delete, historial (`stock_history`).
- **`AuthService`**: registro de usuarios.

La lógica de movimientos y mantenimiento está en **`api/routes.py`** (no en servicio dedicado).

### 4.4 Repositorios

- **`StockRepository`**: queries, filtros por `deleted_at`, búsqueda paginada, `exists_barcode`.

### 4.5 Modelos principales (`api/models.py`)

| Modelo | Uso |
|--------|-----|
| `User` | `user_type`: `admin` \| `user` |
| `Stock` | Inventario; `deleted_at` (soft delete); `version` (optimistic locking) |
| `StockMovement` | Entradas/salidas |
| `MaintenanceRecord` | Mantenimientos |
| `StockHistory` | Auditoría (create, soft_delete, …) |
| `ItemRequest` | Solicitudes de préstamo/uso de elementos |
| `CustomStockType` / `CustomDeviceType` | Tipos personalizados |

---

## 5. Autenticación y autorización

### JWT

- **Access token**: corto (~15 min), en respuesta JSON; el frontend lo guarda en `localStorage` (`jwt_token`).
- **Refresh token**: cookie HTTP-only; renovación con `POST /api/auth/refresh`.
- Cliente centralizado: `frontend/src/api/client.js` (`apiFetch`) reintenta con refresh en 401.

### RBAC

Decorador `@role_required('admin')` en `api/utils.py`:

- Usado en: `users.py` (todo el blueprint), `PATCH /api/solicitudes/<id>`.
- Comprueba `User.user_type` en backend (no solo en frontend).

### Roles

| Rol | Acceso frontend | API |
|-----|-----------------|-----|
| **user** | `/solicitar`, login | Sus solicitudes; no inventario ni usuarios |
| **admin** | Todas las rutas | Todo + gestión usuarios y aprobación solicitudes |

---

## 6. Stock: comportamiento actual

### Creación (`POST /api/stock`)

1. Validaciones en `StockService.create_stock_item` (barcode, inventario, modelo, cantidad, tipo dispositivo).
2. Alta de `Stock`, movimiento inicial (`entrada`) y registro en `stock_history`.
3. **`db.session.commit()`** en la ruta (no usa `db.session.begin()` anidado).

### Consulta

- `GET /api/stock/<barcode>` — detalle + últimos movimientos y mantenimiento.
- `GET /api/stock/search` — paginada (`page`, `per_page`, `q`, `type`, `status`, `location`); excluye soft-deleted.
- `GET /api/stock/inventory` — resumen por tipo + detalle.
- `GET /api/stock/search_es` — Elasticsearch (opcional).

### Soft delete (`DELETE /api/stock/<id>`)

- Marca `deleted_at`; registra en `stock_history`; commit en ruta.
- Listados y búsquedas excluyen registros con `deleted_at` no nulo.

### Optimistic locking

- Columna `Stock.version`.
- `POST /api/stock/<id>/movement` y `POST /api/stock/<id>/maintenance` hacen `UPDATE … WHERE version = ?`.
- Si no afecta filas → **409 Conflict** (`code: conflict`).

### Paginación API (usuarios y solicitudes)

Respuesta estándar:
```json
{
  "items": [...],
  "users|solicitudes": [...],
  "total": 100,
  "page": 1,
  "pages": 5,
  "per_page": 20
}
```
Alias (`users`, `solicitudes`) para compatibilidad con el frontend.

---

## 7. Frontend: rutas y permisos

Definidas en `frontend/src/App.js`:

| Ruta | Componente | Acceso |
|------|------------|--------|
| `/login` | Login | Público |
| `/` | NewInventory | Solo admin (`adminOnly`) |
| `/consultar` | ConsultInventory | Solo admin |
| `/solicitar` | SolicitarElementos | Cualquier usuario autenticado |
| `/admin` | UserDashboard | Solo admin (`requireAdmin`) |
| `*` | — | Redirige a `/solicitar` |

**Comportamiento por rol:**

- Usuario **no admin** entra tras login en **`/solicitar`** (no ve Nuevo/Consultar inventario).
- Usuario **admin** ve menú completo en `Header.js`.

### Componentes clave

| Componente | Función |
|------------|---------|
| `ProtectedRoute` | Redirige a `/login` o `/solicitar` según rol |
| `NewInventory` | Escaneo código (Quagga2/ZXing), alta vía `POST /api/stock` |
| `ConsultInventory` | React Query + búsqueda/filtros paginados |
| `SolicitarElementos` | Crear y listar solicitudes; admin aprueba/rechaza |
| `UserDashboard` | Gestión usuarios (`/api/users`) |
| `AuthStore` | Token, username, user_type en localStorage; verificación periódica |

---

## 8. Flujos de usuario

### Login
```
/login → POST /api/auth/login
       → access_token + refresh (cookie)
       → localStorage: jwt_token, username, user_type
       → admin: /  |  user: /solicitar (vía ProtectedRoute)
```

### Crear stock (admin)
```
/ → escanear o subir imagen → formulario → POST /api/stock
  → Stock + movimiento + stock_history → commit
```

### Consultar inventario (admin)
```
/consultar → GET /api/stock/search (React Query, paginación)
           → filtros por tipo, estado, ubicación
```

### Solicitar elementos (user)
```
/solicitar → GET /api/stock/search?per_page=200 (selector opcional)
           → POST /api/solicitudes
           → GET /api/solicitudes (solo las propias)
```

### Gestionar solicitudes (admin)
```
/solicitar → GET /api/solicitudes (todas, paginadas)
           → PATCH /api/solicitudes/<id> { status, delivery_date }
```

### Gestión usuarios (admin)
```
/admin → GET/POST/PUT/DELETE /api/users
```

---

## 9. API: referencia rápida

**Base:** `http://localhost:9001/api` (Nginx) o `http://localhost:3000/api` (directo).

### Auth
| Método | Ruta | Notas |
|--------|------|-------|
| POST | `/api/auth/login` | Body: username, password |
| POST | `/api/auth/refresh` | Cookie refresh |
| POST | `/api/auth/logout` | |
| POST | `/api/auth/register` | |
| GET | `/api/auth/me` | Usuario actual |

### Stock
| Método | Ruta | Notas |
|--------|------|-------|
| POST | `/api/stock` | Crear |
| GET | `/api/stock/<barcode>` | Detalle |
| GET | `/api/stock/search` | Paginada |
| GET | `/api/stock/search_es` | Elasticsearch |
| GET | `/api/stock/inventory` | Resumen |
| DELETE | `/api/stock/<id>` | Soft delete |
| POST | `/api/stock/<id>/movement` | 409 si conflicto de versión |
| POST | `/api/stock/<id>/maintenance` | 409 si conflicto de versión |
| GET/POST | `/api/stock/types` | Tipos enum + custom |

### Usuarios (admin)
| Método | Ruta | Notas |
|--------|------|-------|
| GET | `/api/users?page=&per_page=` | Paginado |
| POST | `/api/users` | Crear |
| GET/PUT/DELETE | `/api/users/<id>` | |

### Solicitudes
| Método | Ruta | Notas |
|--------|------|-------|
| GET | `/api/solicitudes?page=&per_page=` | Propias o todas (admin) |
| POST | `/api/solicitudes` | Crear |
| PATCH | `/api/solicitudes/<id>` | Solo admin |

### Ops
| Método | Ruta | Notas |
|--------|------|-------|
| GET | `/health` | Solo DB |
| GET | `/ready` | DB + Redis |
| GET | `/api-docs` | Swagger |

---

## 10. CI/CD actual

Workflow **CI** (`.github/workflows/ci.yml`):

- **backend:** Python 3.11, `pytest tests/ -v --cov=src` (SQLite memoria vía config `testing`).
- **frontend:** Node 18, `npm ci`, `npm run build` con `CI=true`.

Ramas: `main`, `development`.

---

## 11. Estado vs. mejoras futuras

### Implementado y estable

- [x] Capas Rutas → Servicios → Repositorios
- [x] JWT access + refresh en cookie
- [x] RBAC `@role_required('admin')`
- [x] Soft delete + `stock_history`
- [x] Optimistic locking en movimiento/mantenimiento (409)
- [x] Paginación en `/api/users` y `/api/solicitudes`
- [x] Health `/health` y readiness `/ready`
- [x] Migraciones Flask-Migrate (sin `create_all` en prod)
- [x] 33 tests pytest
- [x] CI GitHub Actions

### Limitaciones / deuda conocida

| Área | Estado actual | Posible mejora |
|------|---------------|----------------|
| Roles | Solo `admin` / `user` | RBAC granular por permiso |
| Frontend auth | Access en localStorage | Cookie HTTP-only + CSRF |
| Transacciones | Commit en rutas; sin `begin()` anidado | Unificar patrón transaccional en servicios |
| Movimientos/mantenimiento | Lógica en rutas, no en servicio | Extraer a `StockService` |
| Solicitudes | Sin notificaciones | Email/webhooks al aprobar |
| Elasticsearch | Opcional, no indexación automática | Sync al crear/actualizar stock |
| Frontend duplicado | Carpeta `src/` raíz con React legacy | Eliminar o documentar como obsoleto |
| Tests frontend | Jest presente, cobertura limitada | Ampliar tests de componentes |
| App móvil / offline | No existe | PWA o app nativa |
| Producción | Orientado a demo/dev | Hardening según [SECURITY.md](SECURITY.md) |

### Ideas de evolución (backlog sugerido)

1. **Inventario:** edición inline de stock; historial visible en UI; export CSV/PDF.
2. **Solicitudes:** workflow multi-estado; asignación de responsable; enlace con movimientos de salida automáticos al aprobar.
3. **Observabilidad:** métricas Prometheus, tracing, logs estructurados en prod.
4. **Despliegue:** pipeline CD, secrets en vault, checklist automatizado post-deploy.
5. **UX:** unificar uso de `apiFetch` en todos los componentes (algunos usan `fetch` directo).

---

## 12. Documentación relacionada

| Documento | Contenido |
|-----------|-----------|
| [README.md](README.md) | Instalación, badges, resumen |
| [FUNCIONAMIENTO.md](FUNCIONAMIENTO.md) | Guía de flujos (puede quedar desactualizada en detalles) |
| [TECH_DECISIONS.md](TECH_DECISIONS.md) | Porqué de decisiones técnicas |
| [SECURITY.md](SECURITY.md) | Buenas prácticas de seguridad |
| [IMPLEMENTATION_SUMMARY.md](IMPLEMENTATION_SUMMARY.md) | Resumen de implementación |

---

## 13. Resumen operativo

| Objetivo | Comando / URL |
|----------|----------------|
| Arrancar stack | `docker-compose up -d` |
| Migraciones | `python -m flask db upgrade` |
| Admin inicial | `scripts/init_db.py` o servicio `db-init` |
| Tests | `python -m pytest tests/ -v` |
| API docs | http://localhost:9001/api-docs |
| App | http://localhost:9001 |
| Health | http://localhost:3000/health |
| Ready | http://localhost:3000/ready |
