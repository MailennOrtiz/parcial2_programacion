# Spec Delta

## Purpose

Define el comportamiento observable del ciclo de vida de la aplicación FastAPI: creación y cierre del motor asincrónico, fábrica de sesiones, lectura de la URL de la base desde el entorno e inicialización del esquema al arrancar.

## ADDED Requirements

### Requirement: Engine and session factory created on startup
The system SHALL create an asynchronous SQLAlchemy engine and a session factory during application startup, and store both in `app.state`.

#### Scenario: Startup initializes state
- **WHEN** the application starts
- **THEN** `app.state.engine` and `app.state.session_factory` are available for the rest of the process

### Requirement: Engine closed on shutdown
The system SHALL dispose the engine when the application shuts down.

#### Scenario: Shutdown disposes engine
- **WHEN** the application shuts down
- **THEN** the engine is disposed and no further connections are opened

### Requirement: One session per request with expire_on_commit False
The system SHALL provide a `get_session` dependency that yields a single asynchronous session per request, created with `expire_on_commit=False`, and closes it after the request.

#### Scenario: Request gets a session
- **WHEN** a handler declares `Depends(get_session)`
- **THEN** it receives one async session created with `expire_on_commit=False`, and the session is closed when the request ends

### Requirement: DATABASE_URL read from environment
The system SHALL read `DATABASE_URL` from the environment (loaded from `.env`); if it is missing, startup SHALL fail rather than use a default.

#### Scenario: Missing DATABASE_URL fails startup
- **WHEN** the application starts without `DATABASE_URL`
- **THEN** startup fails with an error and the application does not serve requests

### Requirement: Schema created on startup
The system SHALL invoke `SQLModel.metadata.create_all` during startup, after importing all table models, creating only the tables that do not exist.

#### Scenario: Empty database gets schema
- **WHEN** the application starts against a database without the project tables
- **THEN** all project tables are created and startup succeeds

#### Scenario: Existing tables are not altered
- **WHEN** the application starts against a database that already has the tables
- **THEN** `create_all` does not alter existing tables and startup succeeds