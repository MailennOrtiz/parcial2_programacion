# Proposal

## Why

El segundo ejercicio del parcial exige traducir el modelo de dominio de la librería a tablas relacionales con todas sus restricciones (UNIQUE, CHECK, claves foráneas e índices), declarar la navegación en ambos extremos de cada relación y representar el dinero con `Decimal`. Sin estos modelos, los ejercicios de CRUD, altas con relaciones y lecturas sin N+1 no pueden implementarse ni probarse.

## What Changes

- Se implementan los modelos de tabla en `app/modules/<modulo>/models.py` para `editorial`, `genero`, `autor`, `libro`, `libro_autor`, `cliente`, `perfil_cliente`, `venta` y `renglon_venta`.
- Se declaran las restricciones obligatorias: unicidad de ISBN, email y nombres; CHECK de precios, stock, cantidad, orden y rol; claves foráneas con índice.
- Se declaran relaciones con `Relationship(back_populates=...)` en ambos extremos; `Cliente.perfil` devuelve un objeto.
- Se registra la importación de todos los modelos en `app/core/modelos.py` para que `create_all` cree el esquema al arrancar.
- El dinero se representa con `Decimal` (`Numeric`), nunca con `float`.

## Capabilities

### New Capabilities
- `domain-model`: modelos de tabla del dominio de la librería, sus restricciones (UNIQUE, CHECK, claves foráneas e índices) y la navegación bidireccional de todas las relaciones, con dinero en `Decimal`.

### Modified Capabilities
<!-- Ninguna: no hay specs previas en main. -->

## Impact

- Código afectado: `app/modules/*/models.py` y `app/core/modelos.py`.
- Esquema: creación automática de las 9 tablas al arrancar sobre una base vacía.
- Dependencias: sin cambios (SQLModel/SQLAlchemy ya instalados en el ejercicio 1).