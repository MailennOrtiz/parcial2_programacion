# Capítulo 4 — el proyecto de la presentación

Proyecto que acompaña a `Capitulo-4-Completo.pptx` (19 diapositivas). Junta en un solo esquema
lo que antes eran dos proyectos: `proyecto-relaciones parte 4` (Partes 1 y 2, las relaciones) y
`proyecto-buenas-practicas parte2` (Parte 3, el esquema en la práctica). Los originales no se
tocaron.

Stack: FastAPI, SQLModel sobre SQLAlchemy 2 asincrónico, asyncpg y PostgreSQL. No usa Alembic:
las tablas se crean a partir de los modelos con `SQLModel.metadata.create_all`, desde
`reiniciar.py`.

## Puesta en marcha

1. **El `.env`.** Copiar `env.example` a `.env`, en esta misma carpeta, y poner la contraseña real
   en `DATABASE_URL`. La base `capitulo4_db` no hace falta crearla: la crea el paso 3. Si no hay un
   PostgreSQL instalado, `docker compose up -d` levanta uno en el puerto 5433. En ese caso se
   descomenta `POSTGRES_PASSWORD` en el `.env` y se apunta `DATABASE_URL` a `localhost:5433`.

2. **Las dependencias**, en un entorno virtual:

   ```bash
   python -m venv .venv
   .venv\Scripts\activate          # en Linux o macOS: source .venv/bin/activate
   pip install -r requirements.txt
   ```

3. **La base**, como en las diapositivas:

   ```bash
   python reiniciar.py
   ```

   Crea la base si falta, borra todas las tablas, las vuelve a crear desde los modelos y carga los
   datos de los diagramas: Marta (7), Rubén (8), los pedidos 101 a 103, la Empanada, la Gaseosa y
   el Alfajor, y la receta de la Empanada. Se puede correr las veces que haga falta, con el
   servidor andando o apagado. **Antes de cada archivo de `test/` se corre este script**, porque
   los resultados esperados suponen ese punto de partida.

4. **El servidor:**

   ```bash
   python -m uvicorn app.main:app --reload
   ```

   - <http://localhost:8000/> — la página de inicio, con el mapa de diapositivas
   - <http://localhost:8000/static/relaciones.html> — las Partes 1 y 2 con botones
   - <http://localhost:8000/static/buenas-practicas.html> — la Parte 3 con botones
   - <http://localhost:8000/docs> — toda la API

Los archivos `.http` de `test/` se corren con la extensión REST Client de VS Code, petición por
petición. Cada uno trae, en comentarios, qué decir en clase y qué respuesta esperar. Los `.sql` se
corren en pgAdmin (Query Tool) o con `psql`, conectados a `capitulo4_db`.

## Recorrido de las 19 diapositivas

Las diapositivas sin demo son las de portada y las conceptuales: se explican con la presentación
sola.

### Parte 1 — cómo se guarda una relación

| Diap. | Tema | Qué mostrar |
| --- | --- | --- |
| 1 | Portada del capítulo | — |
| 2 | Portada de la Parte 1 | — |
| 3 | En la base no hay asociación, ni agregación, ni composición | — |
| 4 | Cada pedido lleva anotado de quién es (la clave foránea) | `test/01_clave_foranea.http` y `test/02_uno_a_muchos.http`; lo guardado, en `test/00_mirar_la_base.sql` |
| 5 | Uno a uno: clave foránea más unicidad | `test/03_uno_a_uno.http` |
| 6 | Muchos a muchos: la tabla del medio | `test/04_muchos_a_muchos.http` |
| 7 | Agregación y composición: qué pasa al borrar | `test/05_al_borrar.http` (a mitad de camino, `test/05_al_borrar_anular.sql`) y `test/13_composicion_agregacion_asociacion.http` |
| 8 | PostgreSQL no le pone índice a la clave foránea | `test/06_indice_clave_foranea.sql` (carga 60.000 pedidos) |

### Parte 2 — cómo se lee una relación

| Diap. | Tema | Qué mostrar |
| --- | --- | --- |
| 9 | Portada de la Parte 2 | — |
| 10 | En memoria, tres saltos; en la base, tres consultas | — |
| 11 | La relación se declara en los dos extremos | `test/07_declarar_la_relacion.http` |
| 12 | `usuario.pedidos` parece una lista, pero es una consulta | `test/08_declarar_no_es_cargar.http` |
| 13 | Cien pedidos, ciento un viajes (el N+1) | `test/09_n_mas_1.http` |
| 14 | Dos líneas de `selectinload` | `test/11_selectinload.http`; la comparación con `joinedload` de las notas, en `test/12_selectinload_o_joinedload.http` |
| 15 | Acá olvidar la precarga explota (`MissingGreenlet`) | `test/10_sin_precarga_explota.http` |

### Parte 3 — el esquema en la práctica

| Diap. | Tema | Qué mostrar |
| --- | --- | --- |
| 16 | Portada de la Parte 3 | — |
| 17 | El CHECK | `test/14_check.http` y después `test/14_check.sql` |
| 18 | La ventana entre preguntar y escribir | `test/15_unicidad.http` y `python scripts/demo_unicidad.py` (con el servidor corriendo en otra terminal) |
| 19 | Las migraciones (Alembic) | Sin demo: este proyecto no usa Alembic |

## Qué responde un 409

Cuando la base rechaza una escritura, el service responde 409 con un mensaje propio y, al lado,
`mensaje_de_la_base`: el texto crudo de PostgreSQL (`app/core/errores.py`). Se manda a propósito,
para leer en clase el nombre de la restricción que habló (`pedido_usuario_id_fkey`,
`perfil_usuario_id_key`, `ix_producto_nombre`).

## Cómo está armado

| Carpeta | Contenido |
| --- | --- |
| `app/core/` | `config.py` (lee el `.env`), `database.py` (motor, pool y contador de consultas), `errores.py` (el 409 con lo que dijo la base), `modelos.py` (importa todos los modelos) |
| `app/modules/` | Un módulo por recurso: `usuarios`, `pedidos`, `productos`, `categorias`, `ingredientes` y `health`. Cada uno tiene `models.py`, `schemas.py`, `service.py` y `router.py` |
| `app/static/` | Las tres páginas con botones |
| `scripts/` | La demo de unicidad con ocho altas simultáneas |
| `test/` | Los archivos de las demos, del `00` al `15` |

Tres decisiones que conviene señalar en clase:

- **El motor no se crea al importar.** Se crea en el `lifespan` de `app/main.py` y se guarda en
  `app.state`. Importar la aplicación no abre conexiones.
- **La aplicación no crea tablas al arrancar.** Las crea `reiniciar.py`, con `create_all`, que es
  también lo que vuelve la base a los datos de las diapositivas.
- **`pedido.usuario_id` no tiene índice, a propósito.** Es el punto de partida del experimento de
  la diapositiva 8. `test/06` lo agrega a mano y compara los planes de ejecución.

## Errores frecuentes

- **`RuntimeError: Falta la variable DATABASE_URL`**: falta el `.env`, o no está en esta carpeta.
- **`password authentication failed`**: la contraseña del `.env` no es la del servidor.
- **`relation "usuario" does not exist`** al pedir algo: no se corrió `python reiniciar.py`.
- **`ConnectionDoesNotExistError: connection was closed in the middle of operation`**: la base
  `capitulo4_db` todavía no existe, y se crea con `python reiniciar.py`. El error es confuso:
  PostgreSQL rechaza la conexión con "no existe la base de datos", pero en Windows, con el
  servidor en español, al cliente le llega como una conexión cortada. El mensaje real queda en el
  log de PostgreSQL (`data/log`).
- **Una respuesta distinta de la esperada en un `.http`**: casi siempre es porque la base no
  estaba en su punto de partida. Se corre `python reiniciar.py` y se repite el archivo desde el
  principio.
- **`demo_unicidad.py` da ocho 409**: el nombre quedó cargado de una corrida anterior. Se resuelve
  con `python reiniciar.py`.
- **`demo_unicidad.py` no se conecta a `http://127.0.0.1:8000`**: el servidor no está corriendo.
