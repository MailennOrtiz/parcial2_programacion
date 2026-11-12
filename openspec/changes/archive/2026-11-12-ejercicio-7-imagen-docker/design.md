## Context

La API inicia Uvicorn, crea tablas durante el arranque y comprueba PostgreSQL en `/health/ready`.

## Goals / Non-Goals

El objetivo es construir y ejecutar una sola imagen de aplicación. La instalación de PostgreSQL y la publicación en el VPS quedan fuera del cambio.

## Decisions

- Usar Python 3.12 Alpine e instalar primero los requisitos para aprovechar la caché de capas.
- Copiar solo los requisitos y la aplicación. Ejecutar Uvicorn con un usuario de sistema sin privilegios.
- Consultar readiness con wget sobre IPv4 local. Leer la configuración de PostgreSQL en tiempo de ejecución.

## Risks / Trade-offs

La verificación de arranque y disponibilidad requiere un motor Docker accesible y un PostgreSQL de prueba externo al contenedor de la API.
