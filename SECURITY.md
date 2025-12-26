# 🔒 Guía de Seguridad - Proyecto Stock

## ⚠️ Advertencias Importantes

Este documento describe las mejores prácticas de seguridad para el proyecto. **NUNCA** expongas credenciales, secretos o información sensible en el código o documentación pública.

## 🔑 Variables de Entorno Requeridas

### Producción (OBLIGATORIAS)

Crea un archivo `.env` en la raíz del proyecto con las siguientes variables:

```env
# Flask Security (OBLIGATORIO en producción)
SECRET_KEY=tu-clave-secreta-super-segura-minimo-32-caracteres
JWT_SECRET_KEY=tu-clave-jwt-secreta-diferente-de-secret-key

# Base de Datos (OBLIGATORIO)
DB_USER=tu_usuario_db
DB_PASSWORD=tu_password_db_seguro
DB_NAME=nombre_base_datos

# Usuario Administrador Inicial
ADMIN_USERNAME=admin
ADMIN_PASSWORD=contraseña-super-segura-minimo-12-caracteres

# Elasticsearch
ELASTIC_USERNAME=elastic
ELASTIC_PASSWORD=contraseña-elasticsearch-segura

# CORS (ajustar según tu dominio)
CORS_ORIGINS=https://tu-dominio.com,https://www.tu-dominio.com
```

### Desarrollo (Opcionales)

Para desarrollo local, puedes usar valores por defecto, pero **NUNCA** en producción.

## 🚨 Problemas de Seguridad Comunes

### 1. Credenciales por Defecto

**❌ NUNCA HAGAS:**
- Usar `admin123` como contraseña en producción
- Dejar credenciales por defecto sin cambiar
- Commitear archivos `.env` al repositorio

**✅ HAZ:**
- Cambiar todas las contraseñas por defecto inmediatamente
- Usar contraseñas fuertes (mínimo 12 caracteres, mayúsculas, minúsculas, números, símbolos)
- Generar secret keys aleatorios y seguros

### 2. Secret Keys Hardcodeadas

**❌ NUNCA HAGAS:**
```python
SECRET_KEY = "mi-clave-secreta-123"  # ❌ NUNCA
```

**✅ HAZ:**
```python
SECRET_KEY = os.environ.get('SECRET_KEY')  # ✅ Correcto
if not SECRET_KEY:
    raise ValueError("SECRET_KEY must be set!")
```

### 3. Exponer Credenciales en Documentación

**❌ NUNCA HAGAS:**
- Mostrar contraseñas reales en README
- Incluir tokens de ejemplo reales
- Documentar credenciales por defecto sin advertencias

**✅ HAZ:**
- Usar placeholders: `USERNAME`, `PASSWORD`
- Agregar advertencias de seguridad
- Documentar cómo configurar credenciales seguras

## 🛡️ Mejores Prácticas

### Generar Secret Keys Seguros

```bash
# Python
python -c "import secrets; print(secrets.token_urlsafe(32))"

# OpenSSL
openssl rand -hex 32

# Node.js
node -e "console.log(require('crypto').randomBytes(32).toString('hex'))"
```

### Configurar Variables de Entorno

#### Docker Compose

1. Crea un archivo `.env` en la raíz:
```bash
cp .env.example .env
```

2. Edita `.env` con valores seguros:
```env
SECRET_KEY=$(openssl rand -hex 32)
JWT_SECRET_KEY=$(openssl rand -hex 32)
DB_PASSWORD=$(openssl rand -hex 16)
ADMIN_PASSWORD=tu-contraseña-super-segura
ELASTIC_PASSWORD=$(openssl rand -hex 16)
```

3. Asegúrate de que `.env` esté en `.gitignore`

#### Producción Manual

```bash
export SECRET_KEY="tu-clave-secreta"
export JWT_SECRET_KEY="tu-clave-jwt"
export DB_PASSWORD="tu-password-db"
export ADMIN_PASSWORD="tu-password-admin"
```

## 🔐 Configuración de Base de Datos

### PostgreSQL

```bash
# Crear usuario y base de datos
sudo -u postgres psql
CREATE USER stock_user WITH PASSWORD 'password-seguro';
CREATE DATABASE stock_db OWNER stock_user;
GRANT ALL PRIVILEGES ON DATABASE stock_db TO stock_user;
\q
```

### Cambiar Contraseña de Admin

Después de la primera instalación:

1. Inicia sesión con las credenciales por defecto
2. Ve al panel de administración
3. Cambia la contraseña inmediatamente
4. O usa la API:

```bash
curl -X PUT http://localhost:3000/api/users/1 \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"password": "nueva-contraseña-segura"}'
```

## 🚫 Archivos que NUNCA deben estar en Git

Asegúrate de que estos archivos estén en `.gitignore`:

```
.env
.env.local
.env.production
*.key
*.pem
*.cert
instance/*.db
instance/*.sqlite
secrets/
credentials/
```

## 🔍 Verificación de Seguridad

### Checklist Pre-Producción

- [ ] Todas las variables de entorno están configuradas
- [ ] `SECRET_KEY` es único y aleatorio (mínimo 32 caracteres)
- [ ] `JWT_SECRET_KEY` es diferente de `SECRET_KEY`
- [ ] Contraseñas de base de datos son seguras
- [ ] Contraseña de admin ha sido cambiada
- [ ] Contraseña de Elasticsearch ha sido cambiada
- [ ] CORS está configurado solo para dominios permitidos
- [ ] No hay credenciales hardcodeadas en el código
- [ ] Archivos `.env` no están en el repositorio
- [ ] HTTPS está habilitado en producción
- [ ] Rate limiting está activo
- [ ] Logs no contienen información sensible

## 📝 Reportar Vulnerabilidades

Si encuentras una vulnerabilidad de seguridad, **NO** la reportes públicamente. En su lugar:

1. Envía un email a: [tu-email]
2. O crea un issue privado en GitHub
3. Proporciona detalles suficientes para reproducir el problema
4. Espera confirmación antes de hacer público

## 📚 Recursos Adicionales

- [OWASP Top 10](https://owasp.org/www-project-top-ten/)
- [Flask Security Best Practices](https://flask.palletsprojects.com/en/latest/security/)
- [Docker Security](https://docs.docker.com/engine/security/)

---

**Última actualización:** 2024  
**Versión:** 1.0

