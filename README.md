# Librería — Programación III

API asincrónica de catálogo y ventas con FastAPI, SQLModel y PostgreSQL.

**Integrantes:** completar con nombres y apellidos del grupo antes de la entrega.

## Puesta en marcha local

Requiere Python 3.12 o superior y PostgreSQL 16 o superior. Crear previamente
una base **dedicada** al proyecto y configurar una URL accesible con el driver
`postgresql+asyncpg`. Desde PowerShell:

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
Copy-Item env.example .env
```

Editar `.env` con los datos reales sin compartirlo ni subirlo al repositorio.
Codificar para URL los caracteres especiales de usuario o contraseña. Iniciar:

```powershell
.\.venv\Scripts\python.exe -m uvicorn app.main:app --host 127.0.0.1 --port 8000
```

La aplicación crea las tablas faltantes al arrancar, pero no crea la base de
PostgreSQL y `create_all` no modifica tablas ya existentes. En otra terminal,
solo sobre una base vacía y sin escrituras simultáneas:

```powershell
.\.venv\Scripts\python.exe -m app.datos_iniciales
```

El comando no borra datos y rechaza una base que ya contenga filas de la
librería. Inserta una editorial, un género, dos autores, dos libros y un cliente.
Los identificadores se generan en la base: consultá `/libros/` para obtenerlos.
El comando también muestra el identificador del cliente y los de ambos libros.

Documentación interactiva: <http://127.0.0.1:8000/docs>. Comprobaciones:
`/health/live`, `/health/ready` y `/libros/`.

## Pruebas y despliegue

Las pruebas automatizadas y sus limitaciones están en `test/README.md`.
La configuración para EasyPanel y el despliegue exigido por la consigna están en
`DEPLOY.md`. No incluir `.env`, `.venv` ni `__pycache__` en la entrega.
