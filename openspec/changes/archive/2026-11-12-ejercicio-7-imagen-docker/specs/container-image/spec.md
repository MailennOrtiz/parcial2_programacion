## Purpose

Distribuir la API de la librería en una imagen Docker que se pueda ejecutar con un PostgreSQL externo.

## ADDED Requirements

### Requirement: Construcción de la imagen de la API

La imagen SHALL usar `python:3.12-alpine`, instalar `requirements.txt` con `--no-cache-dir` antes de copiar la aplicación y excluir secretos, entornos virtuales, metadatos Git y cachés de Python del contexto.

#### Scenario: Construcción desde el repositorio

- **WHEN** se construye la imagen desde la raíz del repositorio
- **THEN** las dependencias y el código de la API quedan disponibles en la imagen
- **AND** la imagen carece del archivo .env

### Requirement: Ejecución y disponibilidad del contenedor

El contenedor SHALL ejecutar Uvicorn sin privilegios sobre `0.0.0.0:8000`, recibir `DATABASE_URL` en tiempo de ejecución y consultar `/health/ready` por IPv4 local.

#### Scenario: PostgreSQL disponible

- **WHEN** se ejecuta la imagen con una configuración válida y un PostgreSQL disponible
- **THEN** la aplicación crea las tablas y el contenedor pasa a healthy

#### Scenario: Configuración ausente o base inaccesible

- **WHEN** se ejecuta la imagen sin DATABASE_URL o sin conexión a PostgreSQL
- **THEN** el arranque falla
