# Proyecto Stock - Sistema de Gestión de Inventario

Sistema completo de gestión de inventario full-stack desarrollado con Flask, React y React Native. Diseñado para pequeñas y medianas empresas que necesitan control eficiente de su inventario.

## 📊 Badges

![Version](https://img.shields.io/badge/version-0.1.0-blue)
![Build Status](https://img.shields.io/github/actions/workflow/status/ChristianDVillar/proyecto-stock/ci.yml?branch=main&label=build)
![Coverage](https://img.shields.io/codecov/c/github/ChristianDVillar/proyecto-stock?label=coverage)
![Python](https://img.shields.io/badge/python-3.11+-green)
![Node](https://img.shields.io/badge/node-18+-green)
![Flask](https://img.shields.io/badge/Flask-3.0.0-red)
![React](https://img.shields.io/badge/React-18.2.0-blue)
![License](https://img.shields.io/badge/license-MIT-green)
![Docker](https://img.shields.io/badge/docker-ready-blue)
![Code Style](https://img.shields.io/badge/code%20style-black-000000.svg)

## ¿Qué Problema Resuelve?

**Problema:** Las pequeñas empresas y comercios necesitan una solución accesible para gestionar su inventario sin depender de sistemas costosos o complejos.

**Solución:** Proyecto Stock ofrece:
- **Gestión completa de inventario** con códigos de barras
- **Interfaz web moderna** para administración
- **App móvil** para consultas rápidas
- **Autenticación segura** con roles (admin/user)
- **Búsqueda avanzada** con filtros y paginación
- **Trazabilidad** de movimientos y mantenimientos

## Arquitectura

```
┌─────────────┐  ┌─────────────┐  ┌─────────────┐
│  Web App    │  │ Mobile App  │  │ Admin Panel │
│  (React)    │  │(React Native)│ │(Flask-Admin)│
└──────┬──────┘  └──────┬──────┘  └──────┬──────┘
       │                │                 │
       └────────────────┼─────────────────┘
                        │
              ┌─────────▼─────────┐
              │  Backend API      │
              │  (Flask + JWT)    │
              └─────────┬─────────┘
                        │
              ┌─────────▼─────────┐
              │   Database        │
              │ (SQLite/PostgreSQL)│
              └───────────────────┘
```

**Ver arquitectura completa:** [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md)

## Características Principales

### Backend (Flask)
- **Arquitectura modular** con Application Factory Pattern
- **Configuración por entornos** (development/testing/production)
- **JWT Authentication** con renovación automática
- **Rate Limiting** para protección contra abuso
- **Logging estructurado** con JSON
- **Validación robusta** de entrada
- **Tests completos** con pytest (cobertura >80%)
- **Documentación API** con Swagger

### Frontend (React)
- **Patrón Flux** para gestión de estado
- **Componentes modulares** y reutilizables
- **Escaneo de códigos de barras** (cámara e imagen)
- **Búsqueda avanzada** con filtros múltiples
- **Paginación** optimizada
- **Tests con React Testing Library**
- **ESLint + Prettier** para calidad de código

### Mobile (React Native)
- **Autenticación JWT**
- **Consulta de inventario**
- **Búsqueda en tiempo real**
- **Diseño nativo** para iOS y Android

## Requisitos Previos

- **Node.js** >= 18
- **Python** 3.11+
- **PostgreSQL** 15+ (opcional, SQLite por defecto)
- **npm** o **yarn**

## 🚀 Instalación Rápida

### Opción 1: Docker (Recomendado) ⚡

La forma más rápida de iniciar el proyecto:

```bash
# Clonar repositorio
git clone https://github.com/ChristianDVillar/proyecto-stock.git
cd proyecto-stock

# ⚠️ IMPORTANTE: Para producción, crea un archivo .env con valores seguros
# Ver .env.example y SECURITY.md para más información
# Para desarrollo local, puedes usar los valores por defecto

# Construir e iniciar todos los servicios
docker-compose up -d

# Ver logs
docker-compose logs -f
```

> 🔒 **Seguridad:** Los valores por defecto (con sufijo `_dev_only`) son **SOLO para desarrollo**.  
> En **producción**, configura todas las variables de entorno en un archivo `.env`. Ver [SECURITY.md](SECURITY.md).

¡Listo! El proyecto estará disponible en:
- **Frontend**: http://localhost:7000
- **Backend API**: http://localhost:3000
- **Nginx Proxy**: http://localhost:9001
- **API Docs (Swagger)**: http://localhost:9001/api-docs

### Opción 2: Instalación Manual

#### 1. Clonar Repositorio
```bash
git clone https://github.com/ChristianDVillar/proyecto-stock.git
cd proyecto-stock
```

#### 2. Backend
```bash
# Instalar dependencias
pip install -r requirements.txt

# Configurar variables de entorno
cp .env.example .env
# Editar .env con tus configuraciones

# Inicializar base de datos
python src/run.py
```

#### 3. Frontend
```bash
# Instalar dependencias
npm install

# Iniciar servidor de desarrollo
npm start
```

#### 4. Mobile (Opcional)
```bash
cd Stocker/StockerMobile
npm install
npm run android  # o npm run ios
```

## Uso

### Credenciales Iniciales

> ⚠️ **IMPORTANTE:** Las credenciales por defecto solo son para desarrollo. En producción, cambia inmediatamente la contraseña del usuario admin.

Al iniciar la aplicación por primera vez, se crea un usuario administrador por defecto. Consulta la documentación de despliegue para más detalles sobre cómo configurar credenciales seguras en producción.

- **Usuario Regular:** Crear desde panel de administración

### Flujo de Trabajo Típico

1. **Login** → Iniciar sesión con credenciales
2. **Crear Stock** → Escanear código de barras y completar formulario
3. **Consultar** → Buscar items con filtros avanzados
4. **Gestionar** → Ver detalles, movimientos y mantenimientos

### Ejemplos de Uso de API

#### 1. Autenticación y Obtención de Token

```bash
# Login (reemplaza USERNAME y PASSWORD con tus credenciales)
curl -X POST http://localhost:3000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "username": "USERNAME",
    "password": "PASSWORD"
  }'

# Respuesta:
# {
#   "access_token": "eyJ0eXAiOiJKV1QiLCJhbGc...",
#   "user": {
#     "id": 1,
#     "username": "admin",
#     "user_type": "admin"
#   }
# }
```

#### 2. Crear Item de Stock

```bash
# Guardar el token en una variable
TOKEN="tu-token-aqui"

# Crear stock (requiere token)
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

# Respuesta:
# {
#   "message": "Stock creado exitosamente",
#   "stock": {
#     "id": 1,
#     "barcode": "LAP001",
#     "modelo": "Dell XPS 15",
#     ...
#   }
# }
```

#### 3. Buscar Stock

```bash
# Búsqueda simple
curl "http://localhost:3000/api/stock/search?q=laptop&page=1" \
  -H "Authorization: Bearer $TOKEN"

# Búsqueda con filtros avanzados
curl "http://localhost:3000/api/stock/search?q=laptop&dispositivo=laptop&estado=disponible&page=1&per_page=10" \
  -H "Authorization: Bearer $TOKEN"
```

#### 4. Obtener Item por Código de Barras

```bash
# Buscar por código de barras
curl "http://localhost:3000/api/stock/barcode/LAP001" \
  -H "Authorization: Bearer $TOKEN"
```

#### 5. Actualizar Stock

```bash
curl -X PUT http://localhost:3000/api/stock/1 \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "cantidad": 10,
    "estado": "en_uso"
  }'
```

#### 6. Eliminar Stock

```bash
curl -X DELETE http://localhost:3000/api/stock/1 \
  -H "Authorization: Bearer $TOKEN"
```

> 📖 **Documentación completa de la API:** [docs/API.md](docs/API.md)  
> 🔍 **Swagger UI interactivo:** http://localhost:3000/api-docs (o http://localhost:9001/api-docs vía nginx)

## Testing

### Backend
```bash
# Ejecutar todos los tests
pytest

# Con cobertura
pytest --cov=src --cov-report=html

# Tests específicos
pytest tests/test_auth.py -v
pytest tests/test_stock_errors.py -v
```

### Frontend
```bash
# Ejecutar tests
npm test

# Con cobertura
npm test -- --coverage

# Linting
npm run lint
npm run lint:fix

# Formateo
npm run format
```

## Documentación

- **API Documentation:** [docs/API.md](docs/API.md)
- **Deployment Guide:** [docs/DEPLOYMENT.md](docs/DEPLOYMENT.md)
- **Architecture:** [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md)
- **Swagger UI:** http://localhost:3000/api-docs (o http://localhost:9001/api-docs vía nginx)

## Stack Tecnológico

### Backend
- **Flask 3.0.0** - Framework web
- **SQLAlchemy 2.0.25** - ORM
- **Flask-JWT-Extended 4.6.0** - Autenticación
- **Flask-Limiter** - Rate limiting
- **PostgreSQL/SQLite** - Base de datos
- **Gunicorn** - Servidor WSGI
- **Swagger/Flasgger** - Documentación API

### Frontend
- **React 18.2.0** - Biblioteca UI
- **Flux Pattern** - Gestión de estado
- **Quagga2** - Escaneo de códigos de barras
- **React Testing Library** - Testing
- **ESLint + Prettier** - Calidad de código

### Mobile
- **React Native 0.72.0** - Framework móvil
- **TypeScript** - Tipado estático

### DevOps
- **Docker** - Contenedores
- **GitHub Actions** - CI/CD
- **Dependabot** - Actualizaciones automáticas

## Seguridad

- **JWT con expiración** y renovación automática
- **Rate limiting** en endpoints críticos
- **Validación de entrada** en frontend y backend
- **CORS configurado** restrictivamente
- **Variables de entorno** para secretos (nunca hardcodeadas)
- **SQL Injection protection** con ORM
- **Error handling** sin exposición de información sensible

> 🔒 **IMPORTANTE:** Lee [SECURITY.md](SECURITY.md) antes de desplegar en producción.  
> Ver [VULNERABILITIES_REPORT.md](VULNERABILITIES_REPORT.md) para detalles de seguridad.

## Casos de Uso

### Caso 1: Pequeño Comercio
**Escenario:** Tienda de electrónicos necesita controlar inventario de dispositivos.

**Solución:**
1. Admin crea usuarios para empleados
2. Empleados escanean códigos de barras al recibir mercancía
3. Consultan disponibilidad antes de ventas
4. Registran movimientos de stock

### Caso 2: Empresa de Servicios
**Escenario:** Empresa de IT necesita rastrear equipos prestados a clientes.

**Solución:**
1. Registran equipos con códigos de barras
2. Marcan estado (disponible/en_uso)
3. Rastrean ubicación de cada item
4. Registran mantenimientos

## Despliegue

### Docker (Recomendado)

El proyecto incluye configuración completa de Docker con multi-stage builds para desarrollo y producción.

```bash
# Construir todas las imágenes
docker-compose build

# Iniciar todos los servicios
docker-compose up -d

# Ver logs
docker-compose logs -f

# Detener servicios
docker-compose down
```

**Servicios disponibles:**
- **Frontend**: http://localhost:7000
- **Backend API**: http://localhost:3000
- **Nginx (Reverse Proxy)**: http://localhost:9001
- **PostgreSQL**: localhost:5432
- **Elasticsearch**: http://localhost:9200

### Despliegue Manual

Ver guía completa en [docs/DEPLOYMENT.md](docs/DEPLOYMENT.md)

## Roadmap

- [ ] Notificaciones push (mobile)
- [ ] Exportación a Excel/PDF
- [ ] Dashboard con gráficos
- [ ] Integración con sistemas de punto de venta
- [ ] API para terceros
- [ ] Multi-tenant support

## Contribución

Las contribuciones son bienvenidas. Por favor:

1. Fork el proyecto
2. Crea una rama (`git checkout -b feature/AmazingFeature`)
3. Commit tus cambios (`git commit -m 'Add some AmazingFeature'`)
4. Push a la rama (`git push origin feature/AmazingFeature`)
5. Abre un Pull Request

## Licencia

Este proyecto está licenciado bajo la Licencia MIT - ver el archivo [LICENSE](LICENSE) para más detalles.

## Autor

**Christian David Villar Colodro**
- GitHub: [@ChristianDVillar](https://github.com/ChristianDVillar)

## Agradecimientos

- Flask Community
- React Community
- React Native Community
- Todos los contribuidores de las librerías utilizadas

---

**Versión:** 0.1.0  
**Última actualización:** 2024

Para más información, consulta la [documentación completa](docs/).
