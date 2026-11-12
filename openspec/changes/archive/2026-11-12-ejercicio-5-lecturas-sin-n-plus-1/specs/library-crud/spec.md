## MODIFIED Requirements

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