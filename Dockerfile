# Multi-stage build para el backend (server)
FROM python:3.14-slim AS base

WORKDIR /app

# Instalar dependencias del sistema
RUN apt-get update && apt-get install -y \
    gcc \
    postgresql-client \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copiar requirements
COPY requirements.txt .

# Instalar dependencias de Python
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Fase de desarrollo
FROM base AS development

WORKDIR /app

# Copiar código de la aplicación
COPY src/ ./src/
COPY tests/ ./tests/

# Crear directorio instance
RUN mkdir -p instance

# Variables de entorno
ENV FLASK_APP=src/run.py
ENV FLASK_ENV=development
ENV PYTHONUNBUFFERED=1

# Exponer puerto
EXPOSE 5000

# Comando para desarrollo
CMD ["python", "src/run.py"]

# Fase de producción
FROM base AS production

WORKDIR /app

# Copiar código de la aplicación
COPY src/ ./src/
COPY scripts/ ./scripts/

# Crear archivo wsgi.py para Gunicorn
RUN echo "import os\nfrom app import create_app\napp = create_app(os.environ.get('FLASK_ENV', 'production'))" > src/wsgi.py

# Crear directorio instance
RUN mkdir -p instance && \
    chmod 755 instance

# Variables de entorno
ENV FLASK_APP=src/run.py
ENV FLASK_ENV=production
ENV PYTHONUNBUFFERED=1
ENV PORT=3000

# Crear usuario no root
RUN useradd -m -u 1000 appuser && \
    chown -R appuser:appuser /app

USER appuser

# Exponer puerto
EXPOSE 3000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
  CMD curl -f http://localhost:3000/ || exit 1

# Ejecutar con Gunicorn en producción
CMD ["gunicorn", "--bind", "0.0.0.0:3000", "--workers", "4", "--timeout", "120", "--access-logfile", "-", "--error-logfile", "-", "--chdir", "src", "wsgi:app"]

