# Spec Delta

## Purpose

Define the relational domain model of the library (editorials, genres, authors, books, clients, profiles, sales and sale lines) with all required constraints and bidirectional navigation, using Decimal for money.

## ADDED Requirements

### Requirement: Editorial model
The system SHALL define an `editorial` table with `id`, `nombre` and `pais`, where `nombre` is unique and indexed.

#### Scenario: Duplicate editorial name is rejected
- **WHEN** two editorials are inserted with the same `nombre`
- **THEN** the database rejects the second insert with a unique violation

### Requirement: Genre model
The system SHALL define a `genero` table with `id` and `nombre`, where `nombre` is unique and indexed.

#### Scenario: Duplicate genre name is rejected
- **WHEN** two genres are inserted with the same `nombre`
- **THEN** the database rejects the second insert with a unique violation

### Requirement: Author model
The system SHALL define an `autor` table with `id`, `nombre` and `nacionalidad`.

#### Scenario: Author can be created
- **WHEN** an author is inserted with valid `nombre`
- **THEN** the row is persisted with an assigned `id`

### Requirement: Book model with constraints
The system SHALL define a `libro` table with `id`, `isbn`, `titulo`, `precio`, `stock`, `editorial_id` (required) and `genero_id` (nullable), with unique `isbn`, CHECK `precio > 0` and CHECK `stock >= 0`, and indexed foreign keys.

#### Scenario: Non-positive book price is rejected
- **WHEN** a book is inserted with `precio <= 0`
- **THEN** the database rejects the insert with a check violation

#### Scenario: Negative stock is rejected
- **WHEN** a book is inserted with `stock < 0`
- **THEN** the database rejects the insert with a check violation

### Requirement: Book-author association entity
The system SHALL define a `libro_autor` table with composite primary key (`libro_id`, `autor_id`), `rol` restricted to autor/coautor/traductor/ilustrador, and CHECK `orden >= 1`.

#### Scenario: Invalid author role is rejected
- **WHEN** a `libro_autor` row is inserted with a `rol` outside the allowed set
- **THEN** the database rejects the insert with a check violation

#### Scenario: Non-positive order is rejected
- **WHEN** a `libro_autor` row is inserted with `orden < 1`
- **THEN** the database rejects the insert with a check violation

### Requirement: Client model
The system SHALL define a `cliente` table with `id`, `nombre` and `email`, where `email` is unique and indexed.

#### Scenario: Duplicate client email is rejected
- **WHEN** two clients are inserted with the same `email`
- **THEN** the database rejects the second insert with a unique violation

### Requirement: Client profile one-to-one
The system SHALL define a `perfil_cliente` table with `id`, `cliente_id` (unique, indexed), `telefono` and `direccion`, enforcing at most one profile per client.

#### Scenario: Second profile for same client is rejected
- **WHEN** a second `perfil_cliente` is inserted with an existing `cliente_id`
- **THEN** the database rejects the insert with a unique violation

### Requirement: Sale model
The system SHALL define a `venta` table with `id`, `cliente_id` (indexed), `fecha` with timezone and `total` with CHECK `total >= 0`.

#### Scenario: Negative sale total is rejected
- **WHEN** a sale is inserted with `total < 0`
- **THEN** the database rejects the insert with a check violation

### Requirement: Sale line model
The system SHALL define a `renglon_venta` table with `id`, `venta_id` (indexed), `libro_id` (indexed), `cantidad` (CHECK > 0) and `precio_unitario` (CHECK > 0).

#### Scenario: Non-positive quantity is rejected
- **WHEN** a sale line is inserted with `cantidad <= 0`
- **THEN** the database rejects the insert with a check violation

#### Scenario: Non-positive unit price is rejected
- **WHEN** a sale line is inserted with `precio_unitario <= 0`
- **THEN** the database rejects the insert with a check violation

### Requirement: Bidirectional navigation
The system SHALL declare `Relationship(back_populates=...)` on both ends of every foreign key, and `Cliente.perfil` SHALL resolve to a single object rather than a collection.

#### Scenario: Book exposes its editorial and authors
- **WHEN** a book is loaded with its relationships
- **THEN** `libro.editorial` and `libro.autorias` are available without lazy loading

### Requirement: Money as Decimal
The system SHALL represent money columns (`precio`, `total`, `precio_unitario`) using `Decimal`/`Numeric`, never `float`.

#### Scenario: Decimal precision is preserved
- **WHEN** a book price is stored as `25000.00`
- **THEN** it is retrieved with the same decimal value

### Requirement: Models registered before schema creation
The system SHALL import all domain models in `app/core/modelos.py` so that `SQLModel.metadata.create_all` creates every table at startup.

#### Scenario: All tables are created on startup
- **WHEN** the application starts against an empty database
- **THEN** all nine domain tables are created