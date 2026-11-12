# library-crud Specification

## Purpose
TBD - created by archiving change ejercicio-3-contratos-crud. Update Purpose after archive.

## Requirements

### Requirement: Contratos independientes
El sistema SHALL usar contratos de entrada y salida separados de los modelos de tabla, sin `id` en los DTO de creación.

#### Scenario: Alta con datos inválidos
- **WHEN** una petición de creación incumple el contrato
- **THEN** el sistema responde 422 sin guardar el recurso

### Requirement: Operaciones HTTP y errores
El sistema SHALL ofrecer los endpoints de referencia del parcial, responder 201 al crear, 404 ante recursos inexistentes y 409 ante conflictos de integridad, sin exponer errores internos de la base.

#### Scenario: Dato único duplicado
- **WHEN** la base rechaza un dato duplicado
- **THEN** el sistema revierte la transacción y responde 409 con un mensaje propio

### Requirement: Actualización parcial
El sistema SHALL actualizar en PATCH solo los campos enviados y SHALL NOT ofrecer PATCH de ventas.

#### Scenario: Campo omitido
- **WHEN** una actualización omite un campo
- **THEN** el valor previamente guardado permanece sin cambios

### Requirement: Listados y búsqueda
El sistema SHALL paginar todos los listados con `limit` entre 1 y 100, por defecto 20, y `offset` desde 0. El listado de libros SHALL admitir filtro por título sin distinguir mayúsculas y por género, usando parámetros ligados.

#### Scenario: Paginación inválida
- **WHEN** `limit` u `offset` están fuera de sus rangos permitidos
- **THEN** el sistema responde 422

#### Scenario: Búsqueda con texto SQL
- **WHEN** se busca un título que contiene texto con sintaxis SQL
- **THEN** el texto se trata como dato y no como parte de la consulta SQL

### Requirement: Lecturas relacionadas
El sistema SHALL precargar con carga anticipada, en la misma consulta, toda relación que se incluya en una respuesta: `joinedload` para relaciones a uno y `selectinload` para colecciones. Ninguna lectura SHALL depender de carga perezosa. Toda consulta que alimente una respuesta con relaciones SHALL incluir `raiseload("*")` como guardia para detectar accesos perezosos. El detalle de un libro (editorial, género y autores) y el detalle de una venta (cliente y renglones, con libro por renglón) se resolverán con un número fijo de consultas que no crezca con la cantidad de autores o renglones.

#### Scenario: Detalle relacionado
- **WHEN** se solicita un detalle con relaciones
- **THEN** las relaciones necesarias se obtienen mediante carga anticipada

#### Scenario: Detalle de libro relacionado
- **WHEN** se solicita `GET /libros/{id}`
- **THEN** la editorial, el género y las autorías con su autor se obtienen mediante carga anticipada (`joinedload` para editorial y género, `selectinload` para autorías con `joinedload` de autor) y no se ejecutan consultas adicionales al serializar la respuesta.

#### Scenario: Detalle de venta relacionada
- **WHEN** se solicita `GET /ventas/{id}`
- **THEN** el cliente y los renglones con su libro se obtienen mediante carga anticipada (`joinedload` para cliente, `selectinload` para renglones con `joinedload` de libro) y no se ejecutan consultas adicionales al serializar la respuesta.

#### Scenario: Cantidad fija de consultas (C-07)
- **WHEN** se solicita el detalle de un libro o de una venta con 1 vs. N autores o renglones
- **THEN** el número de consultas SQL ejecutadas es idéntico e independiente de N, y no aparecen errores de carga perezosa.
