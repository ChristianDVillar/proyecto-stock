# Decisiones técnicas

Este documento explica el porqué de las decisiones de arquitectura y diseño del proyecto, pensado para revisión técnica y entrevistas.

---

## 1. Soft delete y auditoría

**Qué:** Los ítems de stock no se borran físicamente; se marca `deleted_at` y se registra cada cambio en `stock_history` (acción, old_value, new_value, changed_by).

**Por qué:**
- Trazabilidad y cumplimiento: saber qué existió, quién lo cambió y cuándo.
- Evitar pérdida de datos por borrados accidentales.
- Permitir reportes históricos y auditorías.

**Qué cambiaría si escalara:** Mantenería el patrón; podría particionar `stock_history` por fecha o mover eventos recientes a un almacén de eventos (event sourcing light) para consultas pesadas.

---

## 2. JWT + refresh token en cookie HTTP-only

**Qué:** Access token corto (minutos) en respuesta JSON y header `Authorization`; el frontend lo guarda (p. ej. en localStorage en dev). Refresh token solo en cookie HTTP-only; el cliente renueva el access con `POST /api/auth/refresh` sin reenviar credenciales.

**Por qué:**
- Access corto limita la ventana de uso si el token se filtra.
- Refresh en cookie no accesible desde JavaScript reduce superficie de ataque XSS para ese token.
- En producción se puede migrar también el access a cookie HTTP-only + CSRF token para endurecer frente a XSS.

---

## 3. Rate limiting con Redis

**Qué:** Límites por minuto/hora en login y API (`RATELIMIT_STORAGE_URL=redis://...`). En desarrollo puede usarse memoria; en Docker/producción, Redis.

**Por qué:**
- Proteger contra fuerza bruta en login y abuso de API.
- Redis permite límites consistentes entre varias instancias del backend (escalado horizontal).

---

## 4. Elasticsearch para búsqueda avanzada

**Qué:** Endpoint `GET /api/stock/search_es?q=...` que consulta un índice en Elasticsearch (multi_match sobre barcode, inventario, modelo, descripción). La fuente de verdad sigue siendo Postgres.

**Por qué:**
- Búsqueda full-text y por relevancia sin sobrecargar la BD transaccional.
- Preparado para crecer en filtros y agregaciones.

**Qué cambiaría si escalara:** Cola asíncrona (Celery/RQ) para indexar tras crear/actualizar/eliminar stock; reintentos con backoff si Elastic falla; o reindexado programado para consistencia eventual.

---

## 5. Control de concurrencia (optimistic locking)

**Qué:** El modelo `Stock` tiene columna `version` (entero). En actualizaciones (movimiento, mantenimiento) se hace `UPDATE ... WHERE id = ? AND version = ?` y se incrementa `version`. Si no se afecta ninguna fila → 409 Conflict (otro usuario/modificación concurrente).

**Por qué:**
- Evitar que dos admins sobrescriban cambios sin aviso (“last write wins”).
- Comportamiento estándar en entornos enterprise.

---

## 6. Paginación consistente

**Qué:** Los listados (usuarios, solicitudes, búsqueda de stock) usan `?page=1&per_page=20` y responden con `{ items, total, page, pages, per_page }` (y alias `users`/`solicitudes` para compatibilidad con el frontend).

**Por qué:**
- Evitar devolver miles de filas de golpe (rendimiento y seguridad).
- Misma forma en todos los endpoints facilita consumo y documentación.

---

## 7. Health y readiness

**Qué:**  
- `GET /health`: comprueba solo BD (SELECT 1).  
- `GET /ready`: comprueba BD y Redis (si está configurado).  
Ambos devuelven 503 si algo falla; formato JSON con `checks` por dependencia.

**Por qué:**
- Estándar en Kubernetes y orquestadores: liveness vs readiness.
- Permite que el balanceador no envíe tráfico a instancias no listas.

---

## 8. RBAC con decorador `@role_required`

**Qué:** Endpoints sensibles (CRUD usuarios, PATCH solicitudes) usan `@jwt_required()` y `@role_required('admin')`, que valida `User.user_type` en el backend.

**Por qué:**
- La autorización no puede depender solo del frontend; el backend debe comprobar el rol en cada petición.

---

## 9. Transacciones en operaciones críticas

**Qué:** Crear stock (alta + movimiento inicial + `stock_history`) y soft delete (marca `deleted_at` + registro en historial) se ejecutan dentro de `with db.session.begin():` para que todo sea atómico.

**Por qué:**
- Evitar estados intermedios inconsistentes si falla un paso a mitad.

---

## 10. Migraciones y admin inicial

**Qué:** Tablas solo con Flask-Migrate (`flask db upgrade`); no hay `db.create_all()` en arranque (salvo en tests). El usuario admin inicial se crea con el script `scripts/init_db.py` (servicio `db-init` en Docker), no en `create_app()`.

**Por qué:**
- Esquema versionado y desplegable de forma controlada.
- Un solo punto de creación del admin evita duplicar lógica y condiciones de carrera.
