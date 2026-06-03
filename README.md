# Proyecto Stock

Aplicación full-stack de gestión de inventario con **arquitectura desacoplada**: autenticación JWT (access + refresh en cookie), control de roles, migraciones versionadas (Flask-Migrate), soft delete, auditoría en base de datos y testing automatizado, dockerizada para despliegue reproducible.

[![CI](https://github.com/ChristianDVillar/proyecto-stock/actions/workflows/ci.yml/badge.svg)](https://github.com/ChristianDVillar/proyecto-stock/actions)
[![License](https://img.shields.io/badge/license-MIT-green)](LICENSE)
[![Python](https://img.shields.io/badge/Python-3.11+-blue)](https://www.python.org/)
[![React](https://img.shields.io/badge/React-18.2.0-blue)](https://reactjs.org/)
[![Flask](https://img.shields.io/badge/Flask-3.0.0-black)](https://flask.palletsprojects.com/)
[![Node](https://img.shields.io/badge/Node-18+-green)](https://nodejs.org/)
[![Docker](https://img.shields.io/badge/Docker-Ready-blue)](docker-compose.yml)

---

## Arquitectura

```
                    ┌─────────────┐
                    │   Nginx     │  :9001  (proxy + headers seguridad)
                    └──────┬──────┘
           ┌───────────────┼───────────────┐
           ▼               ▼               ▼
    ┌────────────┐  ┌────────────┐  ┌────────────┐
    │  Frontend  │  │  /api      │  │ /api-docs  │
    │  (React)   │  │  Backend   │  │  /admin    │
    │  :7000     │  │  (Flask)   │  │            │
    └────────────┘  └──────┬─────┘  └────────────┘
                           │
              ┌────────────┼────────────┐
              ▼            ▼            ▼
        ┌──────────┐ ┌──────────┐ ┌──────────┐
        │ Postgres │ │  Redis   │ │ Elastic  │
        │  :5432   │ │  :6379   │ │  :9200   │
        └──────────┘ └──────────┘ └──────────┘
```

**Backend (capas):** Rutas → Servicios (lógica de negocio) → Repositorios (acceso a datos) → Modelos. Migraciones con Flask-Migrate/Alembic; sin `db.create_all()` en arranque.

## ¿Qué hace el proyecto?

- Gestionar productos y stock (CRUD, búsqueda paginada)
- **Soft delete**: eliminación lógica con `deleted_at` y registro en `stock_history`
- Autenticación JWT: access token corto (15 min) + refresh token en cookie HTTP-only
- Control de roles (admin / user) y rutas protegidas
- Rate limiting (auth 5/min; API 100/h) con Redis en Docker
- Auditoría: tabla `stock_history` con cambios (create, update, soft_delete)

## Decisiones técnicas

| Área | Decisión | Motivo |
|------|----------|--------|
| Auth | JWT access + refresh en cookie | Access corto; refresh no accesible desde JS |
| DB | Flask-Migrate / Alembic | Migraciones versionadas, sin create_all en app |
| Backend | Rutas → Services → Repositories | Testable, mantenible, desacoplado |
| Stock | Soft delete + stock_history | Trazabilidad y buenas prácticas |
| Límites | Rate limit login/API | Redis en producción |
| Frontend | React Router + React Query | Navegación y cache/retry estándar |

## Tecnologías

**Backend:** Python 3.11, Flask 3, SQLAlchemy 2, Flask-JWT-Extended, Flask-Migrate, Flask-Limiter, Flasgger (Swagger)

**Frontend:** React 18, React Router 6, TanStack React Query, Quagga2 (códigos de barras)

**Infra:** Docker Compose (Nginx, Postgres, Redis, Elasticsearch), Gunicorn

## Tests

- **Backend:** pytest; tests de login, creación de stock, permisos admin, soft delete e integración.
- **Frontend:** Jest + React Testing Library.

Ejecutar tests backend con cobertura:
```bash
cd proyecto-stock
pip install -r requirements.txt
PYTHONPATH=src pytest tests/ -v --cov=src --cov-report=term-missing
```

## Seguridad

- Contraseñas con hash (werkzeug); JWT access corto (15 min) + refresh en cookie HTTP-only.
- Rate limiting en auth (5/min) y API (100/h); en Docker con Redis.
- Validación de entradas; CORS configurado; headers de seguridad en Nginx (X-Frame-Options, X-Content-Type-Options, Referrer-Policy).
- Variables sensibles por entorno; ver `.env.example` y [SECURITY.md](SECURITY.md).

## Limitaciones conocidas

- Roles: admin / user (no RBAC granular).
- App móvil no offline.
- Despliegue orientado a desarrollo/demo; producción requiere .env seguro y revisión de [SECURITY.md](SECURITY.md).

## Instalación y uso

### Con Docker (recomendado)

```bash
git clone https://github.com/ChristianDVillar/proyecto-stock.git
cd proyecto-stock
# Copiar .env.example a .env y ajustar valores (producción: valores seguros)
docker-compose up -d
```

Disponible en: **Nginx** http://localhost:9001 (frontend + API), **API Docs** http://localhost:9001/api-docs. Migraciones y usuario admin se aplican vía servicios `migrate` y `db-init`.

### Manual (desarrollo)

**Backend:** Antes del primer arranque, aplicar migraciones (no se usa `db.create_all()`).

En **Windows (PowerShell)**:
```powershell
pip install -r requirements-dev.txt
$env:PYTHONPATH = "src"
$env:FLASK_APP = "src/run.py"
python -m flask db upgrade
python src/run.py
```

En **Linux/macOS**:
```bash
pip install -r requirements-dev.txt
export PYTHONPATH=src FLASK_APP=src/run.py
python -m flask db upgrade
python src/run.py
```

> **Nota:** Usa `python -m flask` para que funcione aunque el comando `flask` no esté en el PATH. En desarrollo sin PostgreSQL usa `requirements-dev.txt` (sin psycopg2); en Python 3.13, Pillow está como `>=11` para evitar errores de compilación.

**Frontend:**
```bash
cd frontend && npm install && npm start
```

## Ejemplos de uso de la API

### Login
```bash
curl -X POST http://localhost:3000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username": "USERNAME", "password": "PASSWORD"}'
```

### Crear stock
```bash
TOKEN="tu-token-aqui"
curl -X POST http://localhost:3000/api/stock \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "barcode": "LAP001",
    "inventario": "INV001",
    "dispositivo": "laptop",
    "modelo": "Dell XPS 15",
    "cantidad": 5,
    "estado": "disponible"
  }'
```

Ver [FUNCIONAMIENTO.md](FUNCIONAMIENTO.md) para más detalles del sistema y flujos.

## Objetivo del proyecto

Este proyecto forma parte de mi portfolio personal y tiene como objetivo:

- Practicar desarrollo full-stack real
- Mostrar organización y estructura de un proyecto completo
- Servir como base para mejoras futuras
- Poder explicarse con claridad en una entrevista técnica

No es un tutorial ni un boilerplate, sino un proyecto trabajado y mejorado de forma iterativa.

## Documentación

- [Funcionamiento del sistema](FUNCIONAMIENTO.md)
- [Decisiones técnicas](TECH_DECISIONS.md)
- [Guía de seguridad](SECURITY.md)
- [Resumen de implementación](IMPLEMENTATION_SUMMARY.md)

## Autor

**Christian David Villar Colodro**  
Desarrollador Full-Stack

## Licencia

MIT License - Ver [LICENSE](LICENSE) para más detalles.

---

**Versión:** 1.0.0  
**Última actualización:** 2026

