## Why

El ejercicio 7 pide una imagen ejecutable de la librería que se conecte a un PostgreSQL externo.

## What Changes

- Agregar el Dockerfile y el filtro del contexto de construcción.
- Documentar la construcción, la ejecución y los chequeos del contenedor.

## Capabilities

### New Capabilities

- `container-image`: empaquetado y ejecución de la API con Docker.

### Modified Capabilities

Ninguna.

## Impact

Agrega archivos de empaquetado en la raíz del repositorio. El despliegue en el VPS corresponde al ejercicio 8.
