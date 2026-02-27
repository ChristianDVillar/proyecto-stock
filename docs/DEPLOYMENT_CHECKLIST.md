# Checklist de despliegue

Lista de comprobación para llevar el proyecto a producción (o a un entorno tipo staging).

---

## 1. Variables de entorno

Definir **siempre** en producción (nunca usar valores por defecto con sufijo `_dev_only`).

| Variable | Obligatoria | Descripción | Ejemplo (no usar en prod) |
|----------|-------------|-------------|---------------------------|
| `SECRET_KEY` | Sí | Clave para sesiones Flask | Valor aleatorio largo |
| `JWT_SECRET_KEY` | Sí | Firma de los JWT | Igual o distinta a SECRET_KEY |
| `DATABASE_URI` | Sí (prod) | URL de PostgreSQL | `postgresql://user:pass@host:5432/dbname` |
| `ADMIN_USERNAME` | Recomendado | Usuario admin inicial | `admin` |
| `ADMIN_PASSWORD` | Sí | Contraseña admin inicial | Contraseña segura |
| `DB_USER` / `DB_PASSWORD` / `DB_NAME` | Con Docker | Credenciales PostgreSQL | Coherentes con DATABASE_URI |
| `CORS_ORIGINS` | Sí si hay frontend | Orígenes permitidos (separados por coma) | `https://tu-dominio.com` |
| `FLASK_ENV` | Sí | Entorno | `production` |
| `RATELIMIT_STORAGE_URL` | Recomendado (prod) | Redis para rate limit distribuido | `redis://localhost:6379/0` |
| `LOG_LEVEL` | Opcional | Nivel de log | `INFO` |

- Crear un `.env` en la raíz (o configurarlas en el sistema/servidor) y **no** subir `.env` a Git.
- Ver `.env.example` si existe y `SECURITY.md` para buenas prácticas.

---

## 2. Base de datos (primera vez)

En producción **no** se usa `db.create_all()`. Las tablas se crean con migraciones.

1. **PostgreSQL** levantado y accesible con el usuario y base que uses en `DATABASE_URI`.
2. **Aplicar migraciones** (una vez por despliegue o al actualizar modelo):
   ```bash
   export PYTHONPATH=src
   export FLASK_APP=src/run.py
   export FLASK_ENV=production
   # Definir DATABASE_URI (o cargar .env)
   flask db upgrade
   ```
   En **PowerShell**:
   ```powershell
   $env:PYTHONPATH = "src"; $env:FLASK_APP = "src/run.py"; $env:FLASK_ENV = "production"
   flask db upgrade
   ```
3. **Usuario admin inicial**: si usas el script `scripts/init_db.py` o el servicio **db-init** en Docker, se crea solo la primera vez. Si desplegás sin Docker, podés ejecutar una vez:
   ```bash
   python scripts/init_db.py
   ```
   (con las mismas variables de entorno, incluido `ADMIN_USERNAME` y `ADMIN_PASSWORD`).

---

## 3. Despliegue con Docker

Orden de arranque que usa `docker-compose`:

1. **postgres** y **elasticsearch** (con healthchecks).
2. **migrate**: ejecuta `flask db upgrade` (crea/actualiza tablas).
3. **db-init**: ejecuta `scripts/init_db.py` (crea usuario admin si no existe).
4. **server** (backend): depende de postgres, migrate y db-init.
5. **client** (frontend) y **nginx**.

Comandos:

```bash
# Crear .env con variables de producción (ver sección 1)
docker-compose up -d
```

Comprobar que los contenedores están en marcha:

```bash
docker-compose ps
```

Comprobar salud del backend:

```bash
curl http://localhost:9001/health
# o el puerto que expongas para nginx
```

---

## 4. Despliegue sin Docker (backend con Gunicorn)

1. Instalar dependencias: `pip install -r requirements.txt` (en Linux; en Windows ver `requirements-dev.txt` si usás SQLite en local).
2. Definir todas las variables de la sección 1.
3. Ejecutar migraciones (sección 2).
4. (Opcional) Ejecutar `python scripts/init_db.py` si no existe el admin.
5. Arrancar con Gunicorn, por ejemplo:
   ```bash
   gunicorn --bind 0.0.0.0:3000 --workers 4 --timeout 120 --chdir src wsgi:app
   ```

---

## 5. Frontend en producción

- Build: `npm run build` en el directorio `frontend/`.
- Configurar la variable `REACT_APP_API_URL` si el frontend no se sirve desde el mismo dominio que la API (por ejemplo, la URL base del backend).
- Si la API está en otro dominio, configurar `CORS_ORIGINS` en el backend con la URL del frontend.

---

## 6. Comprobaciones post-despliegue

- [ ] `GET /health` devuelve 200 y `"database": "ok"`.
- [ ] `POST /api/auth/login` con admin responde 200 y devuelve token.
- [ ] `GET /api/stock/inventory` con `Authorization: Bearer <token>` responde 200.
- [ ] En producción no se usan contraseñas ni claves por defecto (sin `_dev_only`).
- [ ] Logs en formato JSON (o según tu estándar) y nivel adecuado (`LOG_LEVEL`).

---

## 7. Referencias

- **Variables y seguridad**: `SECURITY.md`, `.env.example`.
- **Guía de despliegue detallada**: `docs/DEPLOYMENT.md`.
- **Arquitectura y flujo**: `FUNCIONAMIENTO.md`.
