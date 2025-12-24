# Guía de Migración a Monorepo

Esta guía te ayudará a reorganizar el proyecto en una estructura de monorepo.

## Estructura Actual vs Nueva

### Actual
```
proyecto-stock/
├── src/          # Mezcla de frontend y backend
├── Stocker/      # Mobile
└── tests/        # Tests backend
```

### Nueva (Recomendada)
```
proyecto-stock/
├── backend/      # Todo el código Python/Flask
├── frontend/     # Todo el código React
├── mobile/       # App React Native
└── docs/         # Documentación
```

## Pasos de Migración

### 1. Crear Estructura de Directorios

```bash
mkdir -p backend/src/api backend/tests
mkdir -p frontend/src frontend/public
mkdir -p mobile
mkdir -p docs
```

### 2. Mover Archivos Backend

```bash
# Mover código Python
mv src/api/* backend/src/api/
mv src/app.py backend/src/
mv tests/* backend/tests/
mv requirements.txt backend/
mv pytest.ini backend/

# Mover configuración Docker
# (ya creados en la nueva estructura)
```

### 3. Mover Archivos Frontend

```bash
# Mover código React
mv src/js/* frontend/src/js/
mv src/stores/* frontend/src/stores/
mv src/actions/* frontend/src/actions/
mv src/dispatcher/* frontend/src/dispatcher/
mv src/styles/* frontend/src/styles/
mv src/App.js frontend/src/
mv src/App.css frontend/src/
mv src/index.js frontend/src/
mv src/index.css frontend/src/
mv public/* frontend/public/
mv package.json frontend/
mv package-lock.json frontend/
```

### 4. Mover Mobile

```bash
mv Stocker/StockerMobile/* mobile/
```

### 5. Actualizar Imports

#### Backend
Actualizar imports en `backend/src/app.py`:
```python
# Antes
from api.models import db

# Después (si es necesario)
from src.api.models import db
```

#### Frontend
Actualizar imports en componentes:
```javascript
// Antes
import authStore from '../../stores/AuthStore'

// Después (ajustar según nueva estructura)
import authStore from '../stores/AuthStore'
```

### 6. Actualizar Scripts

#### Backend package.json (si existe)
```json
{
  "scripts": {
    "start": "python src/app.py",
    "test": "pytest tests/",
    "migrate": "flask db upgrade"
  }
}
```

#### Frontend package.json
Ya está actualizado en `frontend/package.json`

### 7. Actualizar Variables de Entorno

Actualizar `.env` con nuevas rutas si es necesario.

### 8. Actualizar CI/CD

Los workflows en `.github/workflows/ci.yml` ya están configurados para la nueva estructura.

## Script de Migración Automática

Puedes usar este script para automatizar la migración:

```bash
#!/bin/bash

# Crear estructura
mkdir -p backend/src/api backend/tests frontend/src frontend/public mobile docs

# Mover backend
cp -r src/api/* backend/src/api/ 2>/dev/null
cp src/app.py backend/src/ 2>/dev/null
cp -r tests/* backend/tests/ 2>/dev/null
cp requirements.txt backend/ 2>/dev/null
cp pytest.ini backend/ 2>/dev/null

# Mover frontend
cp -r src/js frontend/src/ 2>/dev/null
cp -r src/stores frontend/src/ 2>/dev/null
cp -r src/actions frontend/src/ 2>/dev/null
cp -r src/dispatcher frontend/src/ 2>/dev/null
cp -r src/styles frontend/src/ 2>/dev/null
cp src/App.* frontend/src/ 2>/dev/null
cp src/index.* frontend/src/ 2>/dev/null
cp -r public/* frontend/public/ 2>/dev/null

# Mover mobile
cp -r Stocker/StockerMobile/* mobile/ 2>/dev/null

echo "Migración completada. Revisa los archivos y actualiza los imports."
```

## Verificación Post-Migración

1. **Backend:**
   ```bash
   cd backend
   pip install -r requirements.txt
   pytest tests/
   python src/app.py
   ```

2. **Frontend:**
   ```bash
   cd frontend
   npm install
   npm test
   npm start
   ```

3. **Mobile:**
   ```bash
   cd mobile/StockerMobile
   npm install
   npm run android  # o ios
   ```

## Notas Importantes

- ⚠️ Haz backup antes de migrar
- ⚠️ Actualiza todos los imports
- ⚠️ Verifica que los tests pasen
- ⚠️ Actualiza documentación con nuevas rutas
- ⚠️ Actualiza scripts de CI/CD si es necesario

## Rollback

Si necesitas revertir:

```bash
git checkout HEAD -- .
```

O restaura desde tu backup.

