# 📦 Proyecto Stock - Sistema de Gestión de Inventario

Sistema completo de gestión de inventario con aplicación web React, backend Flask y aplicación móvil React Native.

![Version](https://img.shields.io/badge/version-0.1.0-blue)
![Python](https://img.shields.io/badge/python-3.11+-green)
![Node](https://img.shields.io/badge/node-18+-green)
![License](https://img.shields.io/badge/license-Private-red)

## 🚀 Características Principales

- ✅ **Autenticación JWT** - Sistema seguro de autenticación con tokens
- ✅ **Gestión de Inventario** - CRUD completo de items de stock
- ✅ **Escaneo de Códigos de Barras** - Soporte para cámara e imágenes
- ✅ **Búsqueda Avanzada** - Filtros por tipo, estado, ubicación
- ✅ **Paginación** - Optimizado para grandes volúmenes de datos
- ✅ **Documentación API** - Swagger/OpenAPI interactiva
- ✅ **Tests Automatizados** - Backend y frontend con cobertura
- ✅ **CI/CD** - GitHub Actions para despliegue automático
- ✅ **Aplicación Móvil** - React Native para iOS y Android
- ✅ **Logging Estructurado** - Logs JSON para producción
- ✅ **Docker** - Contenedores listos para producción

## 📋 Tabla de Contenidos

- [Instalación](#-instalación)
- [Estructura del Proyecto](#-estructura-del-proyecto)
- [Uso](#-uso)
- [API Documentation](#-documentación-api)
- [Testing](#-testing)
- [Despliegue](#-despliegue)
- [Contribución](#-contribución)

## 🏗️ Estructura del Proyecto

```
proyecto-stock/
├── backend/              # Backend Flask
│   ├── src/             # Código fuente
│   ├── tests/           # Tests
│   ├── Dockerfile       # Imagen Docker
│   └── docker-compose.yml
├── frontend/            # Frontend React
│   ├── src/             # Componentes React
│   └── public/          # Archivos públicos
├── mobile/              # App React Native
│   └── StockerMobile/
├── docs/                # Documentación
│   ├── API.md          # Documentación API
│   └── DEPLOYMENT.md   # Guía de despliegue
└── .github/             # CI/CD workflows
```

## 🔧 Instalación

### Prerrequisitos

- Node.js >= 18
- Python 3.11+
- PostgreSQL 15+ (para producción)
- Docker (opcional)

### Backend

```bash
cd backend
pip install -r requirements.txt
cp .env.example .env
# Editar .env con tus configuraciones
python src/app.py
```

### Frontend

```bash
cd frontend
npm install
npm start
```

### Mobile

```bash
cd mobile/StockerMobile
npm install
npm run android  # o npm run ios
```

## 🎯 Uso

### Inicio Rápido

1. **Iniciar Backend:**
   ```bash
   cd backend
   docker-compose up -d
   ```

2. **Iniciar Frontend:**
   ```bash
   cd frontend
   npm start
   ```

3. **Acceder a la aplicación:**
   - Frontend: http://localhost:3000
   - API Docs: http://localhost:5000/api-docs
   - Backend: http://localhost:5000

### Credenciales por Defecto

- **Usuario Admin:** `admin` / `admin123`
- **Usuario Regular:** Crear desde el panel de administración

## 📚 Documentación API

### Endpoints Principales

#### Autenticación
```http
POST /api/auth/login
POST /api/auth/register
GET  /api/auth/me
```

#### Stock
```http
GET  /api/stock/search?q=query&page=1&per_page=20
POST /api/stock
GET  /api/stock/<barcode>
```

#### Usuarios (Admin)
```http
GET    /api/users
POST   /api/users
PUT    /api/users/<id>
DELETE /api/users/<id>
```

### Ejemplo de Uso

```javascript
// Login
const response = await fetch('http://localhost:5000/api/auth/login', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    username: 'admin',
    password: 'admin123'
  })
});

const { access_token } = await response.json();

// Buscar stock
const stockResponse = await fetch(
  'http://localhost:5000/api/stock/search?q=laptop&page=1',
  {
    headers: { 'Authorization': `Bearer ${access_token}` }
  }
);
```

📖 **Documentación completa:** [docs/API.md](docs/API.md)

## 🧪 Testing

### Backend

```bash
cd backend
pytest tests/ -v --cov=src --cov-report=html
```

### Frontend

```bash
cd frontend
npm test -- --coverage
```

### Tests de Integración

```bash
pytest tests/test_integration.py -v
```

## 🚀 Despliegue

### Docker (Recomendado)

```bash
cd backend
docker-compose up -d
```

### Producción

Ver guía completa en [docs/DEPLOYMENT.md](docs/DEPLOYMENT.md)

#### Variables de Entorno

```env
DATABASE_URI=postgresql://user:password@localhost/dbname
SECRET_KEY=your-secret-key
JWT_SECRET_KEY=your-jwt-secret-key
FLASK_ENV=production
LOG_LEVEL=INFO
```

## 🔒 Seguridad

- ✅ Todas las vulnerabilidades corregidas (ver [VULNERABILITIES_REPORT.md](VULNERABILITIES_REPORT.md))
- ✅ Validación de entrada en frontend y backend
- ✅ Tokens JWT con expiración
- ✅ CORS configurado
- ✅ Variables de entorno para secretos
- ✅ Logging estructurado

## 📊 CI/CD

El proyecto incluye GitHub Actions para:

- ✅ Tests automáticos en push/PR
- ✅ Auditoría de seguridad
- ✅ Build de Docker
- ✅ Cobertura de código

Ver [.github/workflows/ci.yml](.github/workflows/ci.yml)

## 🛠️ Tecnologías

### Backend
- Flask 3.0.0
- SQLAlchemy 2.0.25
- Flask-JWT-Extended 4.6.0
- PostgreSQL
- Gunicorn
- Swagger/Flasgger

### Frontend
- React 18.2.0
- React Router
- Quagga2 (códigos de barras)
- React Testing Library

### Mobile
- React Native 0.72.0
- TypeScript

### DevOps
- Docker & Docker Compose
- GitHub Actions
- Dependabot

## 📝 Ejemplos de Uso

### Crear Stock

```bash
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
```

### Buscar Stock

```bash
curl "http://localhost:5000/api/stock/search?q=laptop&page=1&per_page=20" \
  -H "Authorization: Bearer <token>"
```

## 🤝 Contribución

1. Fork el proyecto
2. Crea una rama (`git checkout -b feature/AmazingFeature`)
3. Commit tus cambios (`git commit -m 'Add some AmazingFeature'`)
4. Push a la rama (`git push origin feature/AmazingFeature`)
5. Abre un Pull Request

## 📄 Licencia

Este proyecto es privado.

## 👥 Autores

- **Christian D. Villar** - [GitHub](https://github.com/ChristianDVillar)

## 🙏 Agradecimientos

- Flask Community
- React Community
- React Native Community

---

**Versión:** 0.1.0  
**Última actualización:** 2024

Para más información, consulta la [documentación completa](docs/).
