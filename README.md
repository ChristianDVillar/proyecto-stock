# Proyecto Stock - Sistema de Gestión de Inventario

Sistema completo de gestión de inventario con aplicación web React y aplicación móvil React Native.

## 🚀 Características

- ✅ Autenticación y autorización con JWT
- ✅ Gestión completa de inventario
- ✅ Escaneo de códigos de barras (cámara e imagen)
- ✅ Búsqueda y filtrado avanzado
- ✅ Paginación en listados
- ✅ Documentación API con Swagger
- ✅ Tests unitarios e integración
- ✅ Aplicación móvil React Native
- ✅ Manejo robusto de errores
- ✅ Variables de entorno para producción

## 📋 Requisitos Previos

- Node.js >= 16
- Python 3.8+
- npm o yarn
- pip

## 🔧 Instalación

### Backend

```bash
# Instalar dependencias de Python
pip install -r requirements.txt

# Configurar variables de entorno
cp .env.example .env
# Editar .env con tus configuraciones

# Inicializar base de datos
python src/app.py
```

### Frontend

```bash
# Instalar dependencias
npm install

# Iniciar servidor de desarrollo
npm start
```

### Aplicación Móvil

```bash
cd Stocker/StockerMobile

# Instalar dependencias
npm install

# Para Android
npm run android

# Para iOS
npm run ios
```

## 🏃 Ejecución

### Backend
```bash
python src/app.py
```
El servidor se ejecutará en `http://localhost:5000`

### Frontend
```bash
npm start
```
La aplicación se abrirá en `http://localhost:3000`

### Documentación API
Accede a la documentación Swagger en: `http://localhost:5000/api-docs`

## 🧪 Testing

### Backend
```bash
# Ejecutar todos los tests
pytest

# Con cobertura
pytest --cov=src --cov-report=html
```

### Frontend
```bash
npm test
```

## 📁 Estructura del Proyecto

```
proyecto-stock/
├── src/
│   ├── api/              # Backend Flask
│   │   ├── models.py     # Modelos de base de datos
│   │   ├── routes.py     # Endpoints API
│   │   ├── auth.py       # Autenticación
│   │   ├── users.py      # Gestión de usuarios
│   │   └── utils.py      # Utilidades y validaciones
│   ├── js/
│   │   └── components/   # Componentes React
│   ├── stores/           # Stores (Flux pattern)
│   └── app.py            # Aplicación Flask principal
├── tests/                # Tests unitarios e integración
├── Stocker/
│   └── StockerMobile/    # Aplicación React Native
└── requirements.txt      # Dependencias Python
```

## 🔐 Seguridad

- ✅ Todas las dependencias vulnerables han sido actualizadas
- ✅ Validación de entrada en frontend y backend
- ✅ Manejo seguro de tokens JWT
- ✅ Variables de entorno para configuración sensible
- ✅ CORS configurado correctamente

Ver `VULNERABILITIES_REPORT.md` para detalles completos.

## 📝 Variables de Entorno

Copia `.env.example` a `.env` y configura:

```env
SECRET_KEY=tu-clave-secreta
JWT_SECRET_KEY=tu-clave-jwt
DATABASE_URI=sqlite:///instance/mi_base_datos.db
CORS_ORIGINS=http://localhost:3000,http://localhost:5000
```

## 🎯 Funcionalidades Principales

### Gestión de Inventario
- Crear nuevo stock con código de barras
- Escaneo de códigos de barras (cámara o imagen)
- Búsqueda avanzada con filtros
- Consulta de inventario con paginación
- Visualización de detalles y movimientos

### Autenticación
- Login/Logout con JWT
- Roles: Admin y User
- Verificación de tokens
- Renovación automática de tokens

### Usuarios (Admin)
- Crear usuarios
- Editar usuarios
- Eliminar usuarios
- Gestionar roles

## 📱 Aplicación Móvil

La aplicación móvil React Native permite:
- Iniciar sesión
- Ver inventario
- Buscar items
- Ver detalles de stock

## 🛠️ Tecnologías

### Frontend
- React 18.2.0
- React Router
- Quagga2 (códigos de barras)
- React Icons

### Backend
- Flask 3.0.0
- SQLAlchemy 2.0.25
- Flask-JWT-Extended 4.6.0
- Flask-CORS
- Swagger/Flasgger

### Mobile
- React Native 0.72.0
- TypeScript

### Testing
- pytest
- pytest-flask
- pytest-cov
- Jest (React)

## 📊 Base de Datos

Por defecto usa SQLite. Para producción, se recomienda PostgreSQL:

```env
DATABASE_URI=postgresql://user:password@localhost/dbname
```

## 🚀 Despliegue

### Producción

1. Configurar variables de entorno de producción
2. Cambiar `JWT_COOKIE_SECURE=True` en producción
3. Configurar CORS con dominios de producción
4. Usar PostgreSQL en lugar de SQLite
5. Configurar HTTPS

## 📄 Licencia

Este proyecto es privado.

## 👥 Contribución

Para contribuir:
1. Fork el proyecto
2. Crea una rama para tu feature
3. Commit tus cambios
4. Push a la rama
5. Abre un Pull Request

## 📞 Soporte

Para soporte, contacta al equipo de desarrollo.

---

**Versión**: 0.1.0  
**Última actualización**: 2024
