# Roadmap comercial

Funcionalidades implementadas y planificadas para convertir el proyecto en producto vendible.

## Fase 1 — Implementada

| Funcionalidad | Backend | Frontend |
|---------------|---------|----------|
| Vencimientos (`expiration_date`, alertas 90/30/7/vencido) | ✅ | ✅ Dashboard |
| Lotes (`batch_number`, trazabilidad API) | ✅ | ✅ Formulario |
| Proveedores (CRUD) | ✅ `/api/suppliers` | ✅ `/proveedores` |
| Stock mínimo / óptimo + indicadores 🟢🟡🔴 | ✅ | ✅ Consultar + Dashboard |
| Órdenes de compra (generar, aprobar, recibir) | ✅ `/api/purchase-orders` | ✅ `/ordenes-compra` |
| Dashboard ejecutivo (KPIs, categorías, movimientos) | ✅ `/api/dashboard/executive` | ✅ `/dashboard` |
| Alérgenos (gluten, lácteos, frutos secos, soja) | ✅ | ✅ Formulario |
| Activos IT (SN, MAC, hostname, asignado) | ✅ | ✅ Formulario |
| Garantías + alertas 30 días | ✅ | ✅ Dashboard |
| Historial activo (eventos + movimientos + mant.) | ✅ `/api/stock/<id>/asset-history` | ✅ Modal en Consultar |

**Migración:** `003_commercial_features.py`

## Fase 2 — Implementada

| Funcionalidad | Backend | Frontend |
|---------------|---------|----------|
| Multiempresa (SaaS): `tenant_id` en entidades clave | ✅ | ✅ JWT + AuthStore |
| Multi-almacén + transferencias | ✅ `/api/warehouses`, `/api/transfers` | ✅ `/almacenes`, `/transferencias` |
| Firma digital en solicitudes (canvas base64) | ✅ `POST /api/solicitudes/<id>/sign` | ✅ SignaturePad en `/solicitar` |
| PWA offline básica (manifest + service worker) | — | ✅ |
| Tenants API (admin) | ✅ `/api/tenants` | — |

**Migración:** `004_saas_warehouse.py` — ejecutar:

```powershell
$env:PYTHONPATH = "src"
$env:FLASK_APP = "src/run.py"
python -m flask db upgrade
```

### Pendiente Fase 2 (futuro)

- App móvil (Capacitor): escaneo, entradas/salidas
- Cola offline de movimientos con sincronización
- Firma digital en entregas (PDF)
- Integración carta digital / QR (Dakinis)

## Fase 3 — Planificada

- Predicción de stock (ML)
- OCR de facturas
- Integración ERP
- Notificaciones email/push

## Endpoints (referencia)

```
GET  /api/dashboard/executive
GET  /api/dashboard/expiration-alerts
GET  /api/dashboard/low-stock
GET  /api/dashboard/batches/<batch>/trace

GET|POST|PUT|DELETE  /api/suppliers
GET  /api/suppliers/<id>

GET|POST  /api/purchase-orders
POST     /api/purchase-orders/generate-low-stock
POST     /api/purchase-orders/<id>/approve
POST     /api/purchase-orders/<id>/receive

GET|POST  /api/warehouses
GET      /api/warehouses/<id>/stock

GET|POST  /api/transfers
POST     /api/transfers/<id>/complete

GET|POST  /api/tenants

PATCH    /api/stock/<id>
GET      /api/stock/<id>/asset-history
POST     /api/solicitudes/<id>/sign
```
