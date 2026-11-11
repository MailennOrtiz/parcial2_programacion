## ADDED Requirements

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
El sistema SHALL precargar las relaciones que se incluyan en una respuesta, sin depender de carga perezosa.

#### Scenario: Detalle relacionado
- **WHEN** se solicita un detalle con relaciones
- **THEN** las relaciones necesarias se obtienen mediante carga anticipada
