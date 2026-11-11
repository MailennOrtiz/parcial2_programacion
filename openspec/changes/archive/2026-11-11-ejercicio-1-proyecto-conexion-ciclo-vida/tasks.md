# Tasks

## 1. Estructura del proyecto

- [x] 1.1 Crear el árbol de directorios `app/`, `app/core/`, `app/modules/<modulo>/` para `health`, `editoriales`, `generos`, `autores`, `libros`, `clientes` y `ventas`, más `test/`; verificar que existan los archivos `models.py`, `schemas.py`, `service.py` y `router.py` en cada módulo y `__init__.py` donde corresponda.
- [x] 1.2 Crear `requirements.txt` con las dependencias del stack (FastAPI, SQLModel, SQLAlchemy async, asyncpg, python-dotenv, uvicorn) y `env.example` con la forma de `DATABASE_URL` y `SQL_ECHO` sin secretos; verificar que `pip install -r requirements.txt` finalice sin errores.
- [x] 1.3 Crear `.gitignore` que excluya `.venv`, `__pycache__`, `.env` y `.openspec`; verificar que `git status` no liste esos archivos.

## 2. Configuración y base de datos

- [x] 2.1 Implementar `app/core/config.py` que lea `DATABASE_URL` y `SQL_ECHO` del entorno con `python-dotenv`, sin valores por defecto para `DATABASE_URL`; verificar que importar el módulo sin la variable lance error.
- [x] 2.2 Implementar `app/core/database.py` con `create_async_engine`, `async_sessionmaker` y `get_session` (sesión por petición, `expire_on_commit=False`); verificar que `get_session` sea una dependencia async utilizable con `Depends`.

## 3. Ciclo de vida y aplicación

- [x] 3.1 Implementar `app/main.py` con `lifespan` que cree el motor y la fábrica de sesiones, los guarde en `app.state`, ejecute `SQLModel.metadata.create_all` (importando todos los modelos) y cierre el motor al apagar; verificar que la app arranque y se apague sin errores.
- [x] 3.2 Registrar los routers de `health` (y reservar los de los demás módulos) en `app/main.py`; verificar que `GET /docs` responda 200.

## 4. Endpoints de salud

- [x] 4.1 Implementar `app/modules/health/router.py` con `GET /health/live` devolviendo `{"estado": "vivo"}` sin tocar la base; verificar respuesta 200 con el cuerpo exacto.
- [x] 4.2 Implementar `GET /health/ready` que ejecute `SELECT 1` y responda 200 si la base responde o 503 si falla; verificar ambos casos (base disponible e indisponible).

## 5. Verificación integrada

- [x] 5.1 Levantar el servidor con un `.env` válido y comprobar `GET /health/live` y `GET /health/ready` con HTTP 200; verificar en consola que `create_all` se ejecutó.
- [x] 5.2 Comprobar que sin `DATABASE_URL` el contenedor/proceso termina con error y no queda atendiendo; verificar exit code distinto de cero.