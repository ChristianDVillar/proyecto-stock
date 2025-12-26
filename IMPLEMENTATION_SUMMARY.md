# Implementation Summary

Este documento resume cómo se fue construyendo el proyecto **Proyecto Stock** y las decisiones que se tomaron durante el desarrollo.

El proyecto no nació con una arquitectura cerrada desde el inicio. Fue evolucionando a medida que se iban detectando necesidades reales, problemas de organización y oportunidades de mejora.

---

## Enfoque inicial

La primera versión del proyecto comenzó como una aplicación sencilla para gestionar productos y cantidades de stock. En esta etapa:

- Backend y frontend convivían de forma más acoplada
- No existía una separación clara entre responsabilidades
- El foco estaba en lograr funcionalidad básica

Esta fase fue clave para entender qué partes del sistema necesitaban más atención.

---

## Evolución de la arquitectura

A medida que el proyecto creció, se decidió separar claramente:

- Backend (API REST)
- Frontend web
- Aplicación móvil

Esta separación permitió:
- Mejorar la mantenibilidad
- Reducir dependencias innecesarias
- Facilitar futuras mejoras o cambios tecnológicos

No se optó por una arquitectura compleja (microservicios, colas, etc.) ya que no aportaba valor real para el alcance del proyecto.

---

## Backend

El backend se desarrolló con Flask por su simplicidad y flexibilidad.

Se implementaron:
- Endpoints REST claros y consistentes
- Autenticación mediante JWT
- Validaciones básicas de datos
- Manejo de errores controlado

La prioridad fue que el código fuese fácil de entender y mantener, incluso para alguien que no haya trabajado previamente en el proyecto.

---

## Frontend web

El frontend se desarrolló en React, priorizando:
- Organización del código
- Componentes claros y reutilizables
- Separación de lógica y presentación

Se implementaron funcionalidades como búsqueda, paginación y escaneo de códigos de barras, siempre intentando evitar complejidad innecesaria.

---

## Aplicación móvil

La aplicación móvil se creó como una extensión natural del proyecto, pensada para un uso más práctico.

No se buscó replicar toda la funcionalidad del frontend web, sino cubrir casos concretos como:
- Escaneo de productos
- Consulta rápida de stock

---

## Testing

Se añadieron tests básicos tanto en backend como en frontend.

El objetivo de los tests no fue alcanzar una cobertura total, sino:
- Proteger la lógica crítica
- Detectar errores evidentes tras cambios
- Tener una base mínima de seguridad al refactorizar

---

## Conclusión

El proyecto se desarrolló de forma iterativa, tomando decisiones pragmáticas en cada etapa.

Más que un ejercicio académico, **Proyecto Stock** refleja cómo se aborda un desarrollo real: con compromisos, ajustes y mejoras progresivas.

