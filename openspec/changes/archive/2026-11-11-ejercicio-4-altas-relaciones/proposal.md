# Proposal: Ejercicio 4 - Altas con relaciones: ids y datos

## Summary
Implementar las altas con relaciones para libros (editorial_id, genero_id y autores con roles y orden) y ventas (cliente_id y renglones de venta copiando precio unitario y calculando total). Cumplir estrictamente con las reglas de negocio RN-04 a RN-07 y delegar fallas de claves foráneas en la base de datos respondiendo 409.

## Problem Statement
El dominio de la librería requiere registrar libros y ventas relacionando entidades existentes o agregando entidades anidadas de forma transaccional (composición y agregación), asegurando integridad referencial en la base de datos y un manejo correcto de códigos de estado HTTP (409 ante violaciones de restricciones).

## Proposed Changes
- Actualizar el módulo de `libros` para recibir y procesar correctamente `editorial_id`, `genero_id` y la lista de `autores` (con `autor_id`, `rol`, `orden`) sin consultas previas de existencia (`if`), delegando en la base y capturando `IntegrityError` para retornar 409.
- Actualizar el módulo de `ventas` para recibir `cliente_id` y `renglones` (con `libro_id` y `cantidad`), copiando el precio unitario actual del libro, calculando el total de la venta y cumpliendo las reglas RN-04 a RN-07.
- Escribir o actualizar los casos de prueba `.http` para cubrir C-04 y C-05 (IDs inexistentes que devuelven 409) y C-06 (Venta válida con 2 renglones, precios copiados y total calculado).

## Impact
- Módulos afectados: `app/modules/libros`, `app/modules/ventas`.
- Pruebas en `test/`.
