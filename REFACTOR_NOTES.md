# Notas del Refactor - Backend

## Estructura Nueva vs Antigua

### Antigua
```
src/
├── app.py (todo mezclado)
├── api/
│   ├── routes.py
│   ├── auth.py
│   └── models.py
```

### Nueva (Profesional)
```
src/
├── app/
│   ├── __init__.py (Factory pattern)
│   ├── config.py (Configuraciones por entorno)
│   ├── logging_config.py
│   ├── errors.py (Manejo centralizado)
│   ├── models.py (mover desde api/)
│   ├── routes/
│   │   ├── __init__.py
│   │   ├── stock.py
│   │   ├── auth.py
│   │   └── users.py
│   └── services/ (opcional, para lógica de negocio)
└── run.py (entry point)
```

## Pasos para Completar el Refactor

1. ✅ Creado `app/__init__.py` con factory pattern
2. ✅ Creado `app/config.py` con configuraciones por entorno
3. ✅ Creado `app/logging_config.py`
4. ✅ Creado `app/errors.py`
5. ✅ Creado `app/routes/__init__.py`
6. ✅ Creado `run.py`

## Pendiente

1. Mover `api/models.py` → `app/models.py` y actualizar imports
2. Mover `api/routes.py` → `app/routes/stock.py` y adaptar
3. Mover `api/auth.py` → `app/routes/auth.py` y adaptar
4. Mover `api/users.py` → `app/routes/users.py` y adaptar
5. Mover `api/utils.py` → `app/utils.py`
6. Actualizar todos los imports en el código
7. Actualizar tests para usar nueva estructura
8. Agregar rate limiting
9. Probar que todo funciona

## Comandos para Migrar

```bash
# Mover archivos
mv src/api/models.py src/app/models.py
mv src/api/routes.py src/app/routes/stock.py
mv src/api/auth.py src/app/routes/auth.py
mv src/api/users.py src/app/routes/users.py
mv src/api/utils.py src/app/utils.py

# Actualizar imports en cada archivo
# Cambiar: from api.models → from app.models
# Cambiar: from .models → from app.models (en routes)
```

## Testing

Después del refactor, ejecutar:
```bash
pytest tests/ -v
python src/run.py
```

