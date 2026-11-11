# Spec Delta

## Purpose

Define el comportamiento observable de los endpoints de salud de la aplicación: un endpoint de viveza que no toca la base y un endpoint de disponibilidad que verifica la base con `SELECT 1`.

## ADDED Requirements

### Requirement: Liveness endpoint
The system SHALL expose `GET /health/live` that returns `{"estado": "vivo"}` with HTTP 200 without accessing the database.

#### Scenario: Liveness responds without DB
- **WHEN** a client sends `GET /health/live`
- **THEN** the response is HTTP 200 with body `{"estado": "vivo"}` and no database query is executed

### Requirement: Readiness endpoint
The system SHALL expose `GET /health/ready` that executes `SELECT 1` against the database and returns HTTP 200 when it succeeds, or HTTP 503 when it fails.

#### Scenario: Database available
- **WHEN** a client sends `GET /health/ready` and the database responds to `SELECT 1`
- **THEN** the response is HTTP 200

#### Scenario: Database unavailable
- **WHEN** a client sends `GET /health/ready` and the database does not respond to `SELECT 1`
- **THEN** the response is HTTP 503