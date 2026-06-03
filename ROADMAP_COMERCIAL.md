# Roadmap comercial

Funcionalidades implementadas y planificadas para convertir el proyecto en producto vendible.

**Estado actual:** ~75–85% MVP comercial · Fases 1–2 + MVP ampliado implementados · CI activo · 33+ tests backend.

---

## Evaluación comercial

El proyecto ya no es un simple sistema de stock: es una **plataforma SaaS de inventario y activos** con multiempresa, multi-almacén, compras, trazabilidad, firma digital y PWA.

| Área | Estado |
|------|--------|
| Core inventario + auditoría | ✅ |
| SaaS multi-tenant | ✅ |
| Comercial (OC, proveedores, márgenes) | ✅ |
| Operaciones (almacenes, transferencias, ubicaciones) | ✅ |
| Movilidad (PWA, escaneo rápido) | ✅ |
| Alertas (Email / Telegram / Discord) | ✅ |
| Monetización (planes + límites) | ✅ base |
| Integraciones (API keys + webhooks) | ✅ |
| Portal cliente | ✅ base |
| QR público + carta alérgenos | ✅ base |

---

## Fase 1 — Implementada

Vencimientos, lotes, proveedores, stock mín/óptimo, órdenes de compra, dashboard, alérgenos, activos IT, garantías, historial activo.

**Migración:** `003_commercial_features.py`

---

## Fase 2 — Implementada

Multi-tenant, multi-almacén, transferencias, firma digital, PWA, tenants API.

**Migración:** `004_saas_warehouse.py`

---

## Fase MVP comercial — Implementada

| # | Funcionalidad | Backend | Frontend |
|---|---------------|---------|----------|
| 1 | **Costes y márgenes** (`purchase_price`, `sale_price`, `average_cost`) | ✅ Dashboard KPIs | ✅ Dashboard + formulario |
| 2 | **Inventario rápido móvil** | ✅ `POST /api/stock/quick-scan` | ✅ `/escaneo` |
| 3 | **Ubicaciones físicas** (`location_code` A-03-02) | ✅ | ✅ Formulario |
| 4 | **Inventarios cíclicos** | ✅ `/api/cyclic-inventory/*` | ✅ `/inventario-ciclico` |
| 5 | **Alertas automáticas** Email/Telegram/Discord | ✅ `/api/alerts` | ✅ `/alertas` |
| 6 | **QR público de producto** | ✅ `/api/public/product/<token>` | ✅ `/p/:token` |
| 7 | **Alérgenos → carta QR** | ✅ `/api/public/menu/<slug>` | — |
| 8 | **Portal cliente** | ✅ `/api/portal/*` | ✅ `/portal` |
| 9 | **Facturación SaaS** (Starter 19€ / Business 49€ / Enterprise 99€) | ✅ `/api/billing/*` | ✅ `/planes` |
| 10 | **API pública + webhooks** | ✅ `/api/v1/*`, `/api/integrations/*` | ✅ `/integraciones` |

**Migración:** `005_mvp_commercial.py`

### Planes SaaS

| Plan | Precio | Usuarios | Almacenes | OC/mes |
|------|--------|----------|-----------|--------|
| Starter | 19€ | 3 | 1 | 50 |
| Pro | 29€ | 5 | 2 | 100 |
| Business | 49€ | 10 | 3 | 200 |
| Enterprise | 99€ | ∞ | ∞ | ∞ |

---

## Pendiente (próximas iteraciones)

- Pasarela de pago real (Stripe) vinculada a planes
- UI admin de tenants multi-empresa
- App Capacitor nativa
- Cola offline con sync de movimientos
- Firma en entregas exportada a PDF
- OCR facturas · Predicción IA · ERP

---

## Migraciones

```powershell
$env:PYTHONPATH = "src"
$env:FLASK_APP = "src/run.py"
python -m flask db upgrade
python scripts/init_db.py
```

---

## Rutas frontend

| Ruta | Pantalla |
|------|----------|
| `/dashboard` | KPIs + márgenes |
| `/escaneo` | Inventario rápido (PWA/móvil) |
| `/inventario-ciclico` | Conteos programados |
| `/alertas` | Email / Telegram / Discord |
| `/planes` | Suscripción SaaS |
| `/integraciones` | API keys + webhooks |
| `/portal` | Portal cliente (usuarios) |
| `/p/:token` | Ficha pública QR (sin login) |

---

## Endpoints nuevos (MVP)

```
POST   /api/stock/quick-scan

GET|PUT  /api/alerts
POST     /api/alerts/check
POST     /api/alerts/test

GET|POST /api/cyclic-inventory/schedules
GET      /api/cyclic-inventory/tasks
POST     /api/cyclic-inventory/tasks/generate
POST     /api/cyclic-inventory/tasks/<id>/complete

GET      /api/public/product/<token>
GET      /api/public/menu/<tenant_slug>

GET      /api/portal/summary|stock|solicitudes|orders

GET      /api/billing/plans|usage
PATCH    /api/billing/plan

GET|POST /api/integrations/api-keys
GET|POST /api/integrations/webhooks

GET      /api/v1/stock
POST     /api/v1/stock/<barcode>/movement
```

### Variables de entorno (alertas)

```
SMTP_HOST, SMTP_PORT, SMTP_USER, SMTP_PASSWORD, SMTP_FROM
TELEGRAM_BOT_TOKEN
DISCORD_WEBHOOK_URL
```

---

## Documentación

- [ESTRUCTURA_Y_FUNCIONAMIENTO_ACTUAL.md](ESTRUCTURA_Y_FUNCIONAMIENTO_ACTUAL.md)
- [FUNCIONAMIENTO.md](FUNCIONAMIENTO.md)
- [README.md](README.md)
