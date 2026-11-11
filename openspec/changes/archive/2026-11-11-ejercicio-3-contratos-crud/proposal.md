# Proposal

## Why

El ejercicio 3 requiere exponer los recursos de la librería con contratos de entrada y salida separados de las tablas, actualización parcial, paginación y respuestas HTTP apropiadas. Los modelos actuales todavía no ofrecen esos endpoints.

## What Changes

- Implementar los contratos, servicios y rutas de los endpoints de referencia para editoriales, géneros, autores, libros, clientes y ventas.
- Validar los datos de entrada, aplicar PATCH con `exclude_unset` y devolver 201, 404, 409 o 422 según corresponda.
- Paginar los listados con `limit` y `offset` y filtrar los libros por título de forma parametrizada y por género.
- Proteger las respuestas de errores internos de la base y precargar explícitamente las relaciones usadas en las respuestas.
- Agregar pruebas de los contratos y endpoints implementados.

## Capabilities

### New Capabilities
- `library-crud`: contratos y endpoints HTTP del catálogo, clientes y ventas, con validación, paginación y traducción de errores.

### Modified Capabilities
- Ninguna.

## Impact

- Código en `app/modules/`, utilidades compartidas en `app/core/` y registro de routers en `app/main.py`.
- Pruebas en `test/`.
- Las altas y lecturas relacionadas se coordinan con los ejercicios 4 y 5; Docker y despliegue quedan fuera de alcance.
