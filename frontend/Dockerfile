# Multi-stage build para el frontend (client)
FROM node:20-bullseye-slim AS base

WORKDIR /app

# Copiar archivos de dependencias
COPY package*.json ./

# Instalar dependencias
RUN npm ci --only=production

# Fase de desarrollo
FROM node:20-bullseye AS development

WORKDIR /app

# Copiar node_modules desde base
COPY --from=base /app/node_modules ./node_modules

# Copiar código fuente
COPY . .

# Exponer puerto
EXPOSE 7000

# Comando para desarrollo
CMD ["npm", "run", "start"]

# Fase de build
FROM node:20-bullseye AS builder

WORKDIR /app

# Copiar archivos de dependencias
COPY package*.json ./

# Instalar todas las dependencias (incluyendo devDependencies)
RUN npm ci

# Copiar código fuente
COPY . .

# Build de producción
RUN npm run build

# Fase de producción con Nginx
FROM nginx:alpine AS production

# Copiar archivos build desde builder
COPY --from=builder /app/build /usr/share/nginx/html

# Copiar configuración personalizada de nginx (opcional)
# COPY nginx.conf /etc/nginx/conf.d/default.conf

# Exponer puerto
EXPOSE 80

# Health check
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
  CMD wget --quiet --tries=1 --spider http://localhost/ || exit 1

# Comando por defecto de nginx
CMD ["nginx", "-g", "daemon off;"]

