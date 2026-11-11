GRUPO: Los PapuVengers y el Galo

INTEGRANTES:
Sanchez, Gonzalo
Fachinelli, Leonel
Ortiz, Mailen
Danna, Gabriel
Mendez, Maximiliano
Avila, Roman

# Veterinaria — Programación III

API con FastAPI, SQLModel y PostgreSQL para el trabajo práctico de las unidades 1 a 4.

## Estado

Aplicación ejecutable con ciclo de vida del motor, sesiones asincrónicas, endpoints
de salud, los seis modelos del dominio, `reiniciar.py` con datos iniciales y
endpoints de dueños, fichas, mascotas, prácticas, turnos y laboratorio sin bloqueos.
La revisión final está aprobada: 72 pruebas automatizadas, regresión de C-01 a C-06
con PostgreSQL y evidencias de C-07, C-08 y C-09. Ver
[test/revision_final.md](test/revision_final.md). Queda revisar y confirmar los
archivos en Git antes de subir la entrega.
Las tablas no se crean al iniciar la aplicación, sino al ejecutar el script de reinicio.
El recorrido completo está en [PLAN_TRABAJO.md](PLAN_TRABAJO.md).

## Requisitos previstos

- Python 3.12 o superior.
- PostgreSQL 16 o superior, con una base exclusiva para este trabajo.
- Dependencias declaradas en `requirements.txt`.

## Puesta en marcha (PowerShell)

Desde la raíz del repositorio:

Primero, con PostgreSQL instalado y en ejecución, creá una base exclusiva para
el TP. En pgAdmin, conectate al servidor, abrí Query Tool sobre la base `postgres`
y ejecutá fuera de una transacción:

```sql
CREATE DATABASE veterinaria_db;
```

Si ya existe la base dedicada, no la vuelvas a crear. Podés verificar la versión
con `SHOW server_version;`: debe ser 16 o superior. Luego prepará Python:

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
Copy-Item env.example .env
```

El último comando es solo para la primera configuración: si ya tenés un `.env`,
conservalo. Editalo con los datos de tu PostgreSQL y una base dedicada al TP:

```dotenv
DATABASE_URL=postgresql+asyncpg://usuario:contrasenia@localhost:5432/veterinaria_db
```

La base debe existir: la aplicación y el script no crean la base de PostgreSQL.
`reiniciar.py` se encarga de las tablas y de los datos iniciales.
Si la contraseña contiene caracteres especiales, deben codificarse para una URL.

### Crear el esquema y cargar datos

**Atención: el siguiente comando borra y recrea las seis tablas del TP y elimina
sus datos anteriores. Confirmá que `DATABASE_URL` apunta a una base exclusiva para
veterinaria antes de ejecutarlo. Preferentemente detené el servidor durante el reinicio.**

```powershell
.\.venv\Scripts\python.exe reiniciar.py
```

El borrado, la creación mediante `SQLModel.metadata.create_all` y la carga se
ejecutan en una sola transacción de PostgreSQL. Si falla la carga, se deshace
también la recreación del esquema. El script cierra el motor al finalizar.
No borra la base completa ni usa `DROP ... CASCADE`; dependencias externas a
las tablas del TP pueden impedir el reinicio.

Datos esperados después de cada reinicio:

| Recurso | Datos iniciales |
| --- | --- |
| Dueños | 1: Ana García (`ana@example.com`); 2: Luis Pérez (`luis@example.com`) |
| Ficha | Una ficha para Ana |
| Mascotas | 1: Toby y 2: Mora, de Ana; 3: Luna, de Luis |
| Prácticas | 1: Consulta (15000.00), 2: Desparasitación (8000.00), 3: Vacuna antirrábica (12000.00), 4: Corte de uñas (5000.00) |
| Turno | 1: Toby, control anual, 2026-11-12 a las 10:30 -03:00; prácticas 1 y 3; total 27000.00 |

Los ids se generan con las secuencias de la base, sin insertar ids manuales.
Los precios del turno se copian del catálogo y el total se calcula con `Decimal`.
`test/00_datos_iniciales.sql` permite verificar los resultados en pgAdmin.

### Iniciar el servidor

```powershell
.\.venv\Scripts\python.exe -m uvicorn app.main:app --host 127.0.0.1 --port 8000
```

- Documentación: <http://localhost:8000/docs>.
- `GET /health/live`: 200 con `{"estado":"vivo"}`, sin tocar la base.
- `GET /health/ready`: ejecuta `SELECT 1`; devuelve 200 si PostgreSQL responde,
  o 503 con un mensaje propio si falla. La consulta tiene un límite de 3 segundos.

Una URL válida permite iniciar el servidor aunque PostgreSQL esté caído: el motor
se crea en el `lifespan`, pero no abre conexiones hasta que se requieren.
Si falta `DATABASE_URL` o usa otro controlador, el inicio falla con un mensaje
de configuración, sin mostrar credenciales. Las variables del entorno tienen
prioridad sobre el `.env` de la raíz, independientemente del directorio de ejecución.

## Pruebas de esta etapa

Instalá también las dependencias de desarrollo (agregan `aiosqlite`, utilizado
solo para la base de pruebas en memoria):

```powershell
.\.venv\Scripts\python.exe -m pip install -r requirements-dev.txt
.\.venv\Scripts\python.exe -m unittest discover -s test -p "test_*.py" -v
```

Las pruebas automatizadas no necesitan PostgreSQL: simulan disponibilidad,
errores y timeout, comprueban el cierre del motor y sesiones por petición.
También comprueban los modelos, las restricciones declaradas, las relaciones y
el SQL generado para PostgreSQL. La carga inicial se prueba sobre SQLite en
memoria con claves foráneas activas; el flujo de reinicio se prueba con dobles.
Las pruebas HTTP del CRUD usan los routers reales y SQLite asincrónico en memoria,
con una base nueva por prueba. No leen el `.env` ni acceden al PostgreSQL del usuario.
Estas pruebas no reemplazan la comprobación de los casos sobre PostgreSQL.
Actualmente hay 72 pruebas automatizadas. Las de turnos incluyen rollback completo,
PK compuesta, precios congelados, un único commit y conteo de consultas de detalle.
SQLite no conserva la zona horaria de sus columnas: la normalización a UTC se
comprueba allí, pero la serialización con zona debe verificarse en PostgreSQL.

Los archivos `.http` se ejecutan con REST Client de VS Code. Antes de cada archivo
del dominio, restablecé la base de pruebas dedicada con `python reiniciar.py`
(recordá que borra datos) y ejecutá las peticiones en orden:

- `test/00_health.http`: salud.
- `test/01_duenios.http`: alta, ficha, PATCH, duplicados y borrado restringido.
- `test/02_mascotas.http`: paginación, detalle con dueño y FK inexistente.
- `test/03_practicas.http`: catálogo, precios inválidos y nombre repetido.
- `test/04_turnos.http`: reserva válida, contratos inválidos, rollback y cascada.
  Completalo con `test/04_turnos_verificar.sql` (solo lectura).
- `test/05_turnos_precarga.http`: turnos con una y tres prácticas para C-07.
- `test/06_laboratorio.http`: stock y salud; indica cómo ejecutar C-09 en simultáneo.
- `test/07_check.http`: validación complementaria del DTO y referencia a C-08 SQL.
- `test/07_check.sql`: UPDATE directo que demuestra el CHECK en PostgreSQL.

La revisión real está documentada en `test/revision_final.md`. Las evidencias están
en `test/evidencia_c07.md`, `test/evidencia_c08.md` y `test/evidencia_c09.md`.

## Endpoints disponibles

| Método | Ruta | Respuesta exitosa |
| --- | --- | --- |
| POST | `/duenios/` | 201, dueño con ficha opcional |
| GET | `/duenios/{id}` | 200, dueño con ficha precargada |
| PATCH | `/duenios/{id}` | 200, actualización solo de campos enviados |
| DELETE | `/duenios/{id}` | 204 sin cuerpo |
| POST | `/duenios/{id}/ficha` | 201, ficha |
| GET | `/duenios/{id}/mascotas` | 200, lista de mascotas |
| POST | `/mascotas/` | 201, mascota con `duenio_id` |
| GET | `/mascotas/` | 200, envoltorio paginado |
| GET | `/mascotas/{id}` | 200, mascota con dueño precargado |
| POST | `/practicas/` | 201, práctica |
| GET | `/practicas/` | 200, catálogo |
| POST | `/turnos/` | 201, turno con mascota, precios copiados y total calculado |
| GET | `/turnos/{id}` | 200, turno con mascota y prácticas precargadas |
| DELETE | `/turnos/{id}` | 204 sin cuerpo, con cascada en la base |
| GET | `/laboratorio/stock/{vacuna}` | 200, vacuna y stock del laboratorio |

Los contratos de alta no aceptan `id` ni otros campos extra. Los emails se validan
y los precios deben ser mayores que cero, con hasta dos decimales.
PATCH admite `{}` y conserva los campos omitidos; `null` explícito responde 422
porque nombre y email no son columnas anulables.

El listado de mascotas admite `page` desde 1 y `size` entre 1 y 100 (por defecto 20).
Devuelve `{ items, total, page, size, pages }` con orden por id. Una página posterior
a la última responde 422. Sin resultados devuelve `items=[]`, `pages=0` y acepta
solo la primera página.

Los recursos inexistentes responden 404, las entradas inválidas 422 y los conflictos
de integridad 409 con mensajes propios. Cada service captura `IntegrityError` y
ejecuta rollback; no se pregunta antes si un email o nombre ya existe. La lectura
del dueño antes de crear una ficha solo permite responder 404 para la ruta, no
comprueba si ya tiene ficha. Esa unicidad la decide la base.

Las respuestas con relaciones usan precarga explícita: `joinedload` para ficha o
dueño y `selectinload` para mascotas de un dueño. Los contratos resumidos evitan
ciclos en la respuesta, y `raiseload("*")` detecta accesos a relaciones no precargadas.

## Reserva de turnos

Ejemplo de `POST /turnos/`:

```json
{
  "mascota_id": 1,
  "fecha": "2026-11-12T10:30:00-03:00",
  "motivo": "Control anual",
  "practicas": [{ "practica_id": 1 }, { "practica_id": 3 }]
}
```

El contrato exige al menos una práctica y una fecha con zona horaria. No admite
`id`, `total` ni precios enviados por el cliente, tampoco dentro de las partes.
El servidor normaliza la fecha a UTC, consulta los precios del catálogo en conjunto,
los copia a `turno_practica` y calcula el total con `Decimal`. Con los datos iniciales,
el total es `"27000.00"`; la respuesta incluye la mascota y el nombre y precio
unitario de cada práctica. El precio reservado no cambia al actualizar el catálogo.

Turno y partes se guardan con un solo commit. Si la mascota o una práctica no
existen, o se repite una práctica, la base rechaza la escritura y el service hace
rollback completo y devuelve 409. Una práctica ausente del catálogo no se omite:
se intenta insertar su id sin inventar un precio, y la columna NOT NULL lo impide.
La FK protege además contra el borrado concurrente de referencias existentes.
La lista del cliente nunca se deduplica; la PK compuesta rechaza las repeticiones.

### Lectura sin N+1 y evidencia C-07

El detalle de un turno emite dos SELECT, independientemente de la cantidad de partes:

1. Turno con mascota mediante `joinedload`.
2. Colección `Turno.practicas` mediante `selectinload`, con `joinedload` de
   `TurnoPractica.practica` para obtener el nombre del catálogo.

La respuesta se construye con relaciones ya cargadas. `populate_existing=True`
permite precargar también el turno recién creado en la misma sesión, y
`raiseload("*")` impide consultas perezosas accidentales.

Para la evidencia de entrega, ejecutá `test/05_turnos_precarga.http` contra PostgreSQL
con `echo=True` (ya configurado). Después de las dos altas, ejecutá cada GET por
separado y guardá el fragmento real de consola con sus dos SELECT. No cuentes BEGIN,
COMMIT o ROLLBACK como consultas SELECT ni incluyas las sentencias de las altas.
La evidencia real obtenida está en [test/evidencia_c07.md](test/evidencia_c07.md):
incluye las respuestas y la transcripción de consola aportadas por el usuario,
con dos SELECT tanto para el turno 2 (una práctica) como para el turno 3 (tres).

PostgreSQL puede consumir ids aun cuando una transacción se deshace: los `.http`
usan los ids de las respuestas nombradas, no suponen que todas las altas produzcan
números consecutivos.

## Laboratorio sin bloqueos y caso C-09

`app/modules/laboratorio/cliente.py` reproduce sin cambios la función sincrónica
de la consigna: espera un segundo con `time.sleep(1)` y devuelve `10 + len(vacuna)`.
El service la invoca mediante `await asyncio.to_thread(...)`, fuera del bucle de
eventos. El handler sigue siendo `async def`. No se usa sesión ni se consulta la base.
Por ejemplo, `/laboratorio/stock/rabia` devuelve `{"vacuna":"rabia","stock":15}`.

Para probar C-09 contra el servidor real, iniciá Uvicorn con **un solo worker**
(el comando de arranque de este README ya usa uno). Varios workers podrían ocultar
un bloqueo al responder salud desde otro proceso. Desde otra terminal:

```powershell
.\.venv\Scripts\python.exe test/c09_concurrencia.py
```

El script envía tres consultas de stock simultáneas y luego consulta `/health/live`.
Exige salud 200 en menos de 0.5 segundos y que las tres consultas de stock todavía
estén pendientes cuando responde. Después verifica los tres stocks y sale con código
0 si todo se cumple, o 1 ante un fallo. No requiere reiniciar la base ni lee el `.env`.

Opcionalmente, para otro puerto o un entorno con distinta latencia:

```powershell
.\.venv\Scripts\python.exe test/c09_concurrencia.py --base-url http://localhost:8001 --limite-salud 0.5
```

Las pruebas automatizadas comprueban la función real y, además, usan una barrera
de sincronización para asegurar que las tres llamadas están dentro de la función
bloqueante antes de pedir salud. Salud responde antes de liberar esos workers.
También verifican que los 17 handlers de la aplicación sean asincrónicos.
La ejecución contra el servidor real también se completó: salud respondió 200
en 0,005 s con las tres consultas pendientes. La salida está en
[test/evidencia_c09.md](test/evidencia_c09.md).

## CHECK directo en PostgreSQL — C-08

Abrí `test/07_check.sql` en Query Tool de pgAdmin, conectado a la base del TP.
Ejecutá cada bloque por separado en la misma conexión:

1. Consultá el precio original de la práctica 1; debe existir esa fila.
2. Ejecutá `BEGIN;`.
3. Ejecutá `UPDATE practica SET precio = 0 WHERE id = 1;`.
4. Debe aparecer un error con SQLSTATE `23514` y la restricción
   `ck_practica_precio_positivo`.
5. Ejecutá **siempre** `ROLLBACK;`, también después del error.
6. Consultá otra vez el precio: debe coincidir con el original.

No ejecutes COMMIT ni todo el archivo como un único bloque: el error esperado
puede detener el envío y dejar pendiente el ROLLBACK. La comprobación real ya se
realizó con PostgreSQL 18.4 y conservó el precio `15000.00`; ver
[test/evidencia_c08.md](test/evidencia_c08.md).
La respuesta 422 de un POST con precio cero solo prueba el DTO, no reemplaza C-08.

## Problemas frecuentes

- **C-09: `All connection attempts failed`:** primero iniciá la API en una terminal
  y esperá `Application startup complete`. Sin cerrar esa terminal, ejecutá en otra:
  ` .\.venv\Scripts\python.exe test/c09_concurrencia.py --base-url http://127.0.0.1:8000`.
  Si elegiste otro puerto, adaptá la URL. El script no inicia el servidor por sí mismo.
- **GET con 422 y `int_parsing` para `{{...response.body.$.id}}`:** tu cliente no
  resolvió la referencia de REST Client. Ejecutá primero el POST nombrado o copiá
  su id real y escribilo directamente en la ruta, por ejemplo `/turnos/2` solo si
  el alta devolvió id 2. No supongas ids consecutivos.
- **`GET /health` devuelve 404:** las rutas son `/health/live` y `/health/ready`.
- **`/health/ready` devuelve 503:** revisá que PostgreSQL esté activo y que la base,
  el usuario, la contraseña y el puerto del `.env` sean correctos. Reiniciá la API
  después de editar el `.env`.
- **Faltan tablas:** ejecutá `reiniciar.py` únicamente sobre una base dedicada,
  recordando que elimina los datos del TP.

## Modelo de datos

| Tabla | Clave foránea y justificación |
| --- | --- |
| `ficha_duenio` | `duenio_id` apunta al dueño. Su `UNIQUE` impide más de una ficha por dueño; un dueño puede no tener ficha. |
| `mascota` | `duenio_id` está del lado muchos: varias mascotas pueden pertenecer al mismo dueño. `RESTRICT` impide borrar un dueño con mascotas. |
| `turno` | `mascota_id` identifica la mascota atendida; una mascota puede tener varios turnos. |
| `turno_practica` | `turno_id` y `practica_id` materializan el muchos a muchos. La PK compuesta impide repetir una práctica en el mismo turno; `precio_unitario` conserva el precio reservado. |

Cada FK tiene relaciones declaradas en ambos extremos con `back_populates`.
`Duenio.ficha` es un objeto opcional; `Turno.practicas` contiene objetos
`TurnoPractica`, no directamente entradas del catálogo.

El borrado de un turno elimina sus filas de `turno_practica` mediante
`ON DELETE CASCADE` en PostgreSQL. `passive_deletes="all"` evita que el ORM
las borre o intente poner su FK en NULL, incluso si están cargadas en memoria.
El catálogo no se borra al eliminar un turno.

Como decisión adicional donde la consigna no fija una política, la ficha se
elimina por cascada al borrar a su dueño; las mascotas con turnos y las prácticas
de catálogo usadas en turnos no pueden borrarse (`RESTRICT`). No hay endpoints
adicionales de borrado por estas decisiones.

### Índices de claves foráneas

Se declaran índices en `mascota.duenio_id`, `turno.mascota_id` y
`turno_practica.practica_id`. La unicidad de `ficha_duenio.duenio_id` ya crea
su índice en PostgreSQL.

`turno_practica.turno_id` no necesita otro índice: la PK compuesta
`(turno_id, practica_id)` crea uno cuyo primer componente es `turno_id`,
que ya permite buscar las prácticas de un turno.

Los importes usan `Decimal` y columnas `NUMERIC` con dos decimales; los precios
tienen `CHECK > 0` y el total `CHECK >= 0`. La fecha del turno se almacena como
`TIMESTAMP WITH TIME ZONE`.

## Estructura

```text
app/
├── main.py
├── core/
│   ├── config.py
│   ├── database.py
│   └── modelos.py
└── modules/
    ├── health/
    ├── duenios/
    ├── mascotas/
    ├── practicas/
    ├── turnos/
    └── laboratorio/
test/
```

Cada módulo cuenta con `models.py`, `schemas.py`, `service.py` y `router.py`.
`FichaDuenio` pertenece a `duenios`; `TurnoPractica`, a `turnos`.
Los módulos `health` y `laboratorio` no tienen tablas propias.

`env.example` contiene únicamente valores de ejemplo. El archivo `.env` y los
entornos virtuales están excluidos de Git.

`teoria_anterior/proyecto-capitulo4-completo/` se conserva sin modificaciones como referencia;
la nueva API se desarrolla en esta raíz.

## Entrega y seguridad

Incluir el código de `app/`, `requirements.txt`, `requirements-dev.txt`, `env.example`,
`reiniciar.py`, este README y `test/` con sus archivos HTTP, SQL y evidencias.
No incluir `.env`, credenciales reales ni `.venv/`.

Antes de confirmar cambios, revisar `git status` y `git diff --cached` después de
agregar los archivos elegidos. En la revisión final todavía no había archivos
rastreados; este asistente no agregó archivos al índice ni creó commits.
La guía de instalación debe poder repetirse con una base vacía dedicada al TP.
