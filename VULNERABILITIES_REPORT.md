# Vulnerabilities Report

Este documento resume los aspectos de seguridad que se revisaron durante el desarrollo del proyecto **Proyecto Stock**.

No se trata de una auditoría profesional, sino de una revisión consciente orientada a buenas prácticas básicas en aplicaciones web.

---

## Autenticación y autorización

- Se utiliza autenticación basada en JWT.
- Los tokens se validan en endpoints protegidos.
- No se implementaron refresh tokens para mantener la solución simple.

⚠️ **Limitación conocida:** los tokens tienen una gestión básica y no están pensados para un entorno de alta seguridad.

---

## Validación de datos

- Se valida la entrada de datos en los endpoints principales.
- Se evita confiar en datos provenientes del cliente.
- Se controlan casos básicos como valores negativos o campos vacíos.

---

## Manejo de errores

- Los errores del servidor no exponen información sensible.
- Se devuelven mensajes genéricos al cliente.
- Los detalles técnicos quedan limitados al backend.

---

## CORS y configuración

- Se configura CORS de forma explícita.
- Las variables sensibles se gestionan mediante variables de entorno.
- No se suben credenciales al repositorio.

---

## Dependencias

- Se revisaron dependencias conocidas con vulnerabilidades públicas.
- Se actualizaron librerías cuando fue necesario.
- No se utilizan paquetes abandonados de forma consciente.

---

## Limitaciones

Este proyecto **no está pensado para producción**, por lo que:

- No incluye rate limiting avanzado
- No implementa protección avanzada contra ataques de fuerza bruta
- No cuenta con auditorías automáticas continuas

Estas decisiones se tomaron para mantener el proyecto entendible y acorde a su objetivo educativo y de portfolio.

---

## Dependencias vulnerables encontradas

Durante el desarrollo se identificaron algunas vulnerabilidades en dependencias transitivas (principalmente del frontend con react-scripts). Se aplicaron overrides en `package.json` para mitigar las más críticas, pero algunas requieren actualizaciones mayores que están fuera del alcance del proyecto.

---

## Notas finales

Este proyecto prioriza la claridad y el aprendizaje sobre la seguridad de nivel empresarial. Para un entorno de producción real, se requerirían medidas adicionales que no se implementaron aquí por diseño.
