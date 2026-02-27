# Revisión técnica para producción

Análisis del proyecto como si fuera a desplegarse en entorno real en empresa. Sirve como hoja de ruta de mejoras priorizadas.

**Evaluación general:** Arquitectura actual 7.5/10 → Con mejoras sugeridas 9/10. Nivel: mid-level sólido.

---

## 1. Arquitectura general

### Lo que está bien
- Separación clara Backend / Frontend
- Docker Compose orquestando servicios
- PostgreSQL en producción
- JWT para auth
- Rate limiting diferenciado (muy buena práctica)
- Swagger documentado
- db-init desacoplado
- Posibilidad de usar Elasticsearch

### Mejora crítica: no usar `db.create_all()` en producción

**Problema actual:** Se ejecuta `db.create_all()` dentro de `create_app()`.

**Riesgos:**
- No hay control de versiones de schema
- No se pueden hacer migraciones reales
- No escalable en equipo
- Riesgo en despliegues concurrentes

**Solución:**
- Usar **Flask-Migrate** + **Alembic**
- Flujo: `flask db init` → `flask db migrate -m "initial"` → `flask db upgrade`
- En Docker: el backend **no** debe crear tablas; un contenedor **migrate** debe ejecutar `flask db upgrade`
- Beneficios: versionado real, deploy seguro, rollback posible

---

## 2. Seguridad

### 2.1 JWT en localStorage
- **Problema:** Vulnerable a XSS; si alguien inyecta JS, puede robar el token.
- **Mejor práctica:** Access token corto (5–15 min), Refresh token en HTTP-only cookie, rotación de refresh token.
- **Intermedio:** JWT corto (30 min) + auto logout real.

### 2.2 Headers de seguridad en Nginx
Añadir (ejemplo en Nginx):
- `X-Frame-Options: DENY`
- `X-Content-Type-Options: nosniff`
- `Referrer-Policy: strict-origin-when-cross-origin`
- CSP (Content-Security-Policy)
- HSTS
- Secure cookies donde aplique

### 2.3 Rate limit
- Limitar por IP
- Limitar por `user_id`
- Logging de intentos fallidos (login, etc.)

---

## 3. Base de datos

### 3.1 Índices
En stock y búsqueda:
- Índice en `barcode`
- Índice en `inventory_type`
- Índice en `device_type`
- Índice en `created_at`
- Índice compuesto si se usan filtros múltiples

Ejemplo: `barcode = db.Column(db.String, index=True)` y migraciones que añadan índices.

### 3.2 Movimientos y mantenimientos
- Asegurar `FOREIGN KEY stock_id REFERENCES stock(id) ON DELETE CASCADE` (o política clara) en tablas `movement` y `maintenance` para no dejar basura relacional.

---

## 4. Elasticsearch
- **Pregunta:** ¿Realmente se necesita?
- Si volumen es bajo (< 200k registros), PostgreSQL con GIN, `tsvector`, ILIKE y extensión trigram puede bastar.
- Elasticsearch añade complejidad, RAM y DevOps.
- Usar solo si: búsqueda full-text real, filtros complejos, escala grande.

---

## 5. Docker / Infraestructura

### Mejoras
- Servicio de **backup automático** (Postgres).
- **Health endpoint** más profundo: no solo “ok”, sino verificar:
  - Query real a DB
  - Ping a Elasticsearch (si se usa)
  - Redis si se añade
- **Logging estructurado** en producción:
  - Log en JSON
  - Separar: access logs, app logs, error logs
  - Opcional: enviar a Loki o ELK.

---

## 6. Backend – Organización interna

- Si toda la lógica está en rutas, es frágil y difícil de testear.
- **Ideal:** capas separadas:
  - `api/` (rutas, validación de entrada)
  - `services/` (lógica de negocio)
  - `repositories/` o acceso a datos encapsulado
  - `models/`
- Mejora testabilidad y mantenimiento.

---

## 7. Testing

**Mínimo recomendable:**
- Tests unitarios (lógica de negocio, servicios)
- Tests de integración/API: login, crear stock, permisos admin
- Herramientas: **pytest**, **factory_boy** (o similar para fixtures)

---

## 8. Frontend

### 8.1 Rutas
- Evitar manejo manual con `window.location.pathname` para todo.
- Usar **React Router** + **ProtectedRoute** + layout system.

### 8.2 Estado y datos
- Stores tipo Flux manual son mantenibles pero más verbosos.
- Valorar **Zustand**, **Redux Toolkit** o **React Query** (cache, refetch, loading, retry) para simplificar `InventoryStore` y llamadas a API.

---

## 9. Escalabilidad

- Actual: 1 backend, 1 DB.
- Si crece: Gunicorn con workers adecuados, Redis para rate limit distribuido, capa de cache, posible read replicas.

---

## 10. Mejoras estratégicas (nivel senior)

- **Soft delete** en entidades críticas.
- **Auditoría:** historial de cambios (ej. tabla `stock_history`: stock_id, changed_by, old_value, new_value, timestamp). Muy valioso en inventario.

---

## 11. Prioridades de implementación

| Prioridad | Mejora | Estado |
|-----------|--------|--------|
| Alta | Migraciones con Alembic (Flask-Migrate) | Hecho: migrate container, sin create_all en prod |
| Alta | Índices en DB | Hecho: barcode, inventario, dispositivo, created_at, deleted_at |
| Alta | Mejorar gestión JWT (token corto / refresh / cookies) | Hecho: access 15 min, refresh en cookie, /refresh y /logout |
| Alta | Separar lógica en servicios | Hecho: AuthService, StockService; rutas delegadas |
| Alta | Tests básicos (login, crear stock, permisos) | Hecho: tests usan create_app('testing') |
| Media | React Router + ProtectedRoute | Hecho: BrowserRouter, Routes, ProtectedRoute |
| Media | React Query para datos de API | Hecho: QueryClientProvider, useQuery en ConsultInventory |
| Media | Logging estructurado | Hecho: JSON en prod (pythonjsonlogger) |
| Media | Healthcheck real (DB) | Hecho: /health con SELECT 1 |
| Futuro | Auditoría / historial | Hecho: StockHistory, record en create_stock |
| Futuro | Soft delete | Hecho: columna deleted_at en Stock |
| Futuro | Redis cache | Pendiente |
| Futuro | Revisión Elasticsearch | Pendiente |

---

*Documento generado a partir de la revisión técnica para producción. Actualizado tras implementación de mejoras.*
