# Proyecto Stock

Proyecto personal de gestión de inventario desarrollado como ejercicio práctico de desarrollo full-stack, cubriendo backend, frontend web y una aplicación móvil sencilla.

La idea de este proyecto no fue "hacerlo todo perfecto", sino construir algo real, funcional y entendible, similar a lo que se puede encontrar en un entorno de trabajo pequeño o medio.

[![CI](https://github.com/ChristianDVillar/proyecto-stock/actions/workflows/ci.yml/badge.svg)](https://github.com/ChristianDVillar/proyecto-stock/actions)
[![License](https://img.shields.io/badge/license-MIT-green)](LICENSE)
[![Python](https://img.shields.io/badge/Python-3.11+-blue)](https://www.python.org/)
[![React](https://img.shields.io/badge/React-18.2.0-blue)](https://reactjs.org/)
[![Flask](https://img.shields.io/badge/Flask-3.0.0-black)](https://flask.palletsprojects.com/)
[![Node](https://img.shields.io/badge/Node-18+-green)](https://nodejs.org/)
[![Docker](https://img.shields.io/badge/Docker-Ready-blue)](docker-compose.yml)

---

## ¿Qué hace el proyecto?

Proyecto Stock permite:

- Gestionar productos y stock
- Crear, editar y eliminar artículos
- Controlar cantidades disponibles
- Buscar y paginar resultados
- Autenticarse mediante usuario y contraseña
- Escanear códigos de barras desde web o móvil

Está pensado como una base sólida, no como un producto final listo para producción.

## Estructura general

El proyecto está dividido en tres partes principales:

- **Backend**: API REST desarrollada con Flask
- **Frontend Web**: Aplicación React para uso desde navegador
- **Aplicación móvil**: App en React Native orientada a escaneo y consulta rápida

La separación se hizo para evitar un enfoque monolítico y para que cada parte pueda evolucionar de forma independiente si fuera necesario.

## Decisiones técnicas (explicadas de forma honesta)

Durante el desarrollo se tomaron varias decisiones conscientes:

- **Se eligió Flask por simplicidad**. No era necesario algo más complejo para el alcance del proyecto.
- **La autenticación se implementó con JWT sin refresh tokens** para mantener el código claro y fácil de seguir.
- **El frontend prioriza legibilidad y orden del código** antes que optimizaciones avanzadas.
- **No se usaron arquitecturas complejas** (microservicios, colas, etc.) porque no aportaban valor real al objetivo del proyecto.
- **La app móvil reutiliza conceptos del frontend web** para evitar duplicar lógica innecesariamente.

La intención fue siempre mantener el equilibrio entre buenas prácticas y simplicidad.

## Tecnologías utilizadas

**Backend:**
- Python
- Flask
- SQLAlchemy
- JWT
- Swagger / OpenAPI

**Frontend Web:**
- React 18
- React Router
- Quagga2 (lector de códigos de barras)
- React Icons

**Aplicación móvil:**
- React Native
- TypeScript

**Testing:**
- pytest (backend)
- Jest / Testing Library (frontend)

## Tests

El proyecto incluye tests básicos tanto en backend como en frontend.

No se buscó una cobertura del 100%, sino asegurar que:
- Los endpoints principales funcionan
- La lógica crítica no se rompe con cambios
- Los componentes clave renderizan correctamente

## Seguridad

Se tuvieron en cuenta aspectos básicos de seguridad habituales en proyectos de este tipo:

- Validación de datos de entrada
- Uso de JWT para autenticación
- Configuración de CORS
- Revisión manual de dependencias vulnerables

Existe un archivo específico ([VULNERABILITIES_REPORT.md](VULNERABILITIES_REPORT.md)) donde se documentan los puntos revisados.

## Limitaciones conocidas

Este proyecto tiene varias limitaciones asumidas a propósito:

- No hay sistema avanzado de roles (solo un esquema simple)
- No se implementaron refresh tokens
- La app móvil no funciona offline
- El despliegue está pensado para entornos de desarrollo o demo

Estas limitaciones se dejaron explícitas para no sobre-complicar el proyecto.

## Instalación y uso

### Con Docker (recomendado)

```bash
git clone https://github.com/ChristianDVillar/proyecto-stock.git
cd proyecto-stock

# ⚠️ Para producción, crea un archivo .env con valores seguros
# Ver SECURITY.md para más información

docker-compose up -d
```

El proyecto estará disponible en:
- Frontend: http://localhost:7000
- Backend API: http://localhost:3000
- Nginx Proxy: http://localhost:9001
- API Docs: http://localhost:9001/api-docs

### Manual

**Backend:**
```bash
pip install -r requirements.txt
python src/run.py
```

**Frontend:**
```bash
cd frontend
npm install
npm start
```

Para más detalles, ver la documentación incluida en el repositorio.

## Ejemplos de uso de la API

### Login
```bash
curl -X POST http://localhost:3000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username": "USERNAME", "password": "PASSWORD"}'
```

### Crear stock
```bash
TOKEN="tu-token-aqui"
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
```

Ver [docs/API.md](docs/API.md) para más ejemplos.

## Objetivo del proyecto

Este proyecto forma parte de mi portfolio personal y tiene como objetivo:

- Practicar desarrollo full-stack real
- Mostrar organización y estructura de un proyecto completo
- Servir como base para mejoras futuras
- Poder explicarse con claridad en una entrevista técnica

No es un tutorial ni un boilerplate, sino un proyecto trabajado y mejorado de forma iterativa.

## Documentación

- [API Documentation](docs/API.md)
- [Deployment Guide](docs/DEPLOYMENT.md)
- [Architecture](docs/ARCHITECTURE.md)
- [Security Guide](SECURITY.md)
- [Implementation Summary](IMPLEMENTATION_SUMMARY.md)

## Autor

**Christian David Villar Colodro**  
Desarrollador Full-Stack

## Licencia

MIT License - Ver [LICENSE](LICENSE) para más detalles.

---

**Versión:** 1.0.0  
**Última actualización:** 2025

