# Proyecto Stock - Sistema de Gestión de Inventario

Sistema completo de gestión de inventario full-stack desarrollado con Flask, React y React Native. Diseñado para pequeñas y medianas empresas que necesitan control eficiente de su inventario.

![Version](https://img.shields.io/badge/version-0.1.0-blue)
![Python](https://img.shields.io/badge/python-3.11+-green)
![Node](https://img.shields.io/badge/node-18+-green)
![Flask](https://img.shields.io/badge/Flask-3.0.0-red)
![React](https://img.shields.io/badge/React-18.2.0-blue)
![License](https://img.shields.io/badge/license-Private-red)

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

## Instalación Rápida

### 1. Clonar Repositorio
```bash
git clone https://github.com/ChristianDVillar/proyecto-stock.git
cd proyecto-stock
```

### 2. Backend
```bash
# Instalar dependencias
pip install -r requirements.txt

# Configurar variables de entorno
cp .env.example .env
# Editar .env con tus configuraciones

# Inicializar base de datos
python src/run.py
```

### 3. Frontend
```bash
# Instalar dependencias
npm install

# Iniciar servidor de desarrollo
npm start
```

### 4. Mobile (Opcional)
```bash
cd Stocker/StockerMobile
npm install
npm run android  # o npm run ios
```

## Uso

### Credenciales por Defecto
- **Usuario Admin:** `admin` / `admin123`
- **Usuario Regular:** Crear desde panel de administración

### Flujo de Trabajo Típico

1. **Login** → Iniciar sesión con credenciales
2. **Crear Stock** → Escanear código de barras y completar formulario
3. **Consultar** → Buscar items con filtros avanzados
4. **Gestionar** → Ver detalles, movimientos y mantenimientos

### Ejemplo de Uso de API

```bash
# Login
curl -X POST http://localhost:5000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username":"admin","password":"admin123"}'

# Crear stock (requiere token)
curl -X POST http://localhost:5000/api/stock \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{
    "barcode": "LAP001",
    "inventario": "INV001",
    "dispositivo": "laptop",
    "modelo": "Dell XPS 15",
    "cantidad": 5
  }'

# Buscar stock
curl "http://localhost:5000/api/stock/search?q=laptop&page=1" \
  -H "Authorization: Bearer <token>"
```

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
- **Swagger UI:** http://localhost:5000/api-docs

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
- **Variables de entorno** para secretos
- **SQL Injection protection** con ORM
- **Error handling** sin exposición de información sensible

Ver [VULNERABILITIES_REPORT.md](VULNERABILITIES_REPORT.md) para detalles de seguridad.

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
```bash
cd backend
docker-compose up -d
```

### Producción
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

Este proyecto es privado.

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
