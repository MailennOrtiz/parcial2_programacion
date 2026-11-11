# Plan de trabajo — API de veterinaria

Referencia: `MiniTP_Cap1a4_Consigna.pdf`.

El proyecto se desarrolla en la raíz del repositorio. La carpeta
`teoria_anterior/proyecto-capitulo4-completo/` se conserva sin modificaciones como referencia.
Se respetan los nombres de tablas, columnas, rutas y módulos de la consigna.

## 1. Estructura y entorno

- [x] Crear `app/`, `app/core/`, los seis módulos funcionales y `test/`.
- [x] Preparar `requirements.txt`, `env.example` y `.gitignore`.
- [x] Verificar Python 3.12 o superior (entorno local: 3.14.6).
- [x] Verificar PostgreSQL 16 o superior.
- [x] Verificar la conexión real (el usuario confirmó HTTP 200 en `/health/ready`).
- [x] Crear un entorno virtual e instalar las dependencias.
- [x] Configurar un `.env` local (configuración realizada por el usuario).
- Control manual permanente: confirmar que la base configurada sea exclusiva para
  veterinaria antes de cada reinicio. El agente no reinició las tablas originales.

Cada módulo tiene `models.py`, `schemas.py`, `service.py` y `router.py`.
`health` y `laboratorio` no requieren tablas; sus archivos de modelos quedan
reservados para mantener la organización uniforme.

## 2. Conexión, ciclo de vida y salud

- [x] Leer `DATABASE_URL` desde el entorno mediante `python-dotenv`.
- [x] Crear el motor asincrónico y la fábrica de sesiones en el `lifespan`.
- [x] Guardarlos en `app.state` y cerrar el motor al apagar.
- [x] Implementar `get_session`: una sesión por petición, mediante `Depends`,
      con `expire_on_commit=False`.
- [x] Implementar `GET /health/live` sin acceder a la base.
- [x] Implementar `GET /health/ready` con `SELECT 1` y respuesta 503 si falla.

Hito: la aplicación arranca y permite verificar su conexión.

Implementación cubierta por nueve pruebas automatizadas sin PostgreSQL, todas
aprobadas. El usuario configuró el `.env` y confirmó HTTP 200 en `/health/ready`.
El agente no creó ni modificó bases de datos en esta etapa.

## 3. Modelos, restricciones y relaciones

- [x] Crear `Duenio` y `FichaDuenio` en `duenios`.
- [x] Crear `Mascota` en `mascotas` y `Practica` en `practicas`.
- [x] Crear `Turno` y `TurnoPractica` en `turnos`.
- [x] Declarar claves foráneas, `UNIQUE`, `CHECK` e índices obligatorios.
- [x] Declarar relaciones bidireccionales con `back_populates`.
- [x] Representar la ficha como objeto opcional, no como lista.
- [x] Usar `Decimal`, las precisiones `NUMERIC` indicadas y fechas con zona horaria.
- [x] Configurar `ON DELETE RESTRICT` para mascotas de un dueño.
- [x] Configurar `ON DELETE CASCADE` para las prácticas de un turno y
      `passive_deletes="all"` sin cascada de borrado del ORM.
- [x] Usar la clave primaria compuesta `(turno_id, practica_id)`.

Diez pruebas adicionales verifican los metadatos, la navegación y el SQL generado
para PostgreSQL sin modificar la base. La comprobación de las restricciones sobre
filas reales se realizará al crear el esquema y ejecutar los casos de prueba.

## 4. Reinicio y datos iniciales

- [x] Implementar `reiniciar.py` para borrar y recrear las tablas con
      `SQLModel.metadata.create_all`, importando previamente todos los modelos.
- [x] Cargar dos dueños, uno con ficha, tres mascotas y cuatro prácticas.
- [x] Cargar un turno con dos prácticas y precios congelados.
- [x] Usar datos deterministas y cerrar el motor al finalizar.
- [x] Documentar que el reinicio elimina los datos de la base configurada.
- [x] Ejecutar el reinicio y verificar los datos sobre PostgreSQL (comprobado
      por el usuario).

Hito: `python reiniciar.py` funciona sobre una base vacía dedicada al TP.

Script implementado; el usuario confirmó la comprobación del reinicio real. Siete pruebas nuevas
comprueban la carga en SQLite en memoria, los ids, precios históricos, repetibilidad,
borrados y el flujo de transacción/cierre mediante dobles. Total: 26 pruebas aprobadas.
`test/00_datos_iniciales.sql` contiene consultas de verificación manual de solo lectura.

## 5. Contratos y endpoints simples

- [x] Separar DTO de entrada y salida de los modelos de tabla; altas sin `id`.
- [x] Implementar dueños y ficha, luego prácticas y mascotas.
- [x] Aplicar PATCH parcial con `exclude_unset=True`.
- [x] Implementar paginación `{ items, total, page, size, pages }`.
- [x] Usar `size=20` por defecto, rango 1 a 100 y página inicial siempre válida.
- [x] Responder 201 al crear, 204 sin cuerpo al borrar, 404 si no existe,
      409 por conflictos de integridad y 422 por contratos inválidos.
- [x] Capturar `IntegrityError`, ejecutar rollback y emitir mensajes propios.
- [x] No comprobar unicidad o restricciones con consultas previas de existencia.

Los routers reciben datos y delegan. La lógica y las consultas viven en los
services, que reciben la sesión como parámetro.

Etapa implementada para dueños, fichas, prácticas y mascotas. Los DTO de turnos
están implementados en la etapa 6. PATCH permite omitir campos pero rechaza null explícito.
La paginación vacía devuelve `pages=0` y acepta `page=1`; no acepta páginas posteriores.
El detalle del dueño usa `joinedload` de ficha; el detalle de mascota usa `joinedload`
de dueño; la colección de mascotas de un dueño usa `selectinload`. `raiseload("*")`
impide depender accidentalmente de otras cargas perezosas en esas consultas.

Se agregaron 19 pruebas HTTP sobre SQLite asincrónico en memoria (45 pruebas totales)
y los archivos `01_duenios.http`, `02_mascotas.http` y `03_practicas.http`. Las pruebas
automatizadas no leen el `.env` ni modifican la base de PostgreSQL del usuario.

## 6. Reserva de turnos

- [x] Recibir mascota, fecha, motivo y lista anidada no vacía de prácticas.
- [x] Consultar en conjunto los precios del catálogo y copiarlos a las filas
      `TurnoPractica`; el cliente no envía precios ni total.
- [x] Calcular el total con `Decimal`.
- [x] Guardar turno y prácticas en una sola transacción: todo o nada.
- [x] Asegurar que una práctica inexistente produce 409 sin guardar nada.
- [x] Dejar que la clave primaria compuesta rechace prácticas repetidas con 409;
      no eliminarlas silenciosamente de la entrada.

Implementados POST, GET y DELETE de turnos. El contrato exige zona horaria y
rechaza precios, total e ids de turno enviados por el cliente. La fecha se normaliza
a UTC antes de guardarla. Una sola consulta obtiene todos los precios; una práctica
ausente conserva su id y llega a la escritura sin precio: la base rechaza el NULL
obligatorio, sin inventar un importe ni omitir la parte. La FK protege también
contra referencias eliminadas concurrentemente. El rollback abarca el turno y todas
sus partes. Las prácticas repetidas llegan intactas a la PK compuesta.

Se agregaron 19 pruebas de turnos (64 pruebas totales), `04_turnos.http`,
`04_turnos_verificar.sql` y `05_turnos_precarga.http`. La validación automatizada
usa SQLite asincrónico en memoria y no modifica PostgreSQL.

## 7. Lecturas sin N+1

- [x] Usar `joinedload` para relaciones a uno y `selectinload` para colecciones.
- [x] Precargar todas las relaciones necesarias para las respuestas, también
      después de las altas y actualizaciones.
- [x] Resolver el detalle del turno con un número fijo de consultas SELECT
      (objetivo: dos), independientemente de la cantidad de prácticas.
- [x] Verificar el detalle de dueño con su ficha sin carga perezosa.
- [x] Activar `echo=True`.
- [x] Guardar evidencia real del caso C-07 sobre PostgreSQL.

Las pruebas cuentan dos SELECT en GET de turno tanto con una como con tres
prácticas: turno con mascota, y partes con entrada del catálogo mediante JOIN.
El archivo `05_turnos_precarga.http` prepara ambos casos para capturar la consola
real. La evidencia de PostgreSQL está en `test/evidencia_c07.md`, con las respuestas
HTTP y la transcripción de los logs aportados por el usuario: dos SELECT para el
turno 2 (una práctica) y dos para el turno 3 (tres prácticas).

## 8. Laboratorio sin bloqueos

- [x] Incorporar `laboratorio/cliente.py` exactamente como aparece en la consigna.
- [x] Ejecutar `consultar_stock` fuera del bucle de eventos mediante
      `asyncio.to_thread`, sin modificar la función sincrónica.
- [x] Implementar `GET /laboratorio/stock/{vacuna}`.
- [x] Verificar que todos los handlers sean `async def`.
- [x] Comprobar que tres consultas simultáneas no retrasen `/health/live`.

Ocho pruebas adicionales (72 en total) comprueban el stock real, el uso de hilos,
el handler y el script de concurrencia. Una prueba sincronizada espera que los
tres workers estén dentro de la función bloqueante y verifica salud antes de
liberarlos; no depende de adivinar una espera inicial. Los 17 handlers son async.

`test/06_laboratorio.http` documenta los endpoints y `test/c09_concurrencia.py`
envía las peticiones simultáneas contra el servidor real con un solo worker.
El script se probó con ASGI aislado y contra el servidor real del usuario:
salud 200 en 0,005 s con tres consultas de stock pendientes. La salida está en
`test/evidencia_c09.md`.

## 9. Pruebas y entrega

- [x] Crear archivos `.http` para C-01 a C-09 con resultados esperados en comentarios.
- [x] Agregar el archivo `.sql` de C-08 y verificaciones SQL de rollback y cascada.
- [x] Preparar una prueba realmente concurrente para C-09.
- [x] Probar lista vacía, prácticas repetidas, PATCH parcial y paginación inválida.
- [x] Verificar que cambiar el precio del catálogo no altere turnos reservados.
- [x] Completar `README.md` con instalación desde cero y ejecución de pruebas.
- [x] Justificar de qué lado va cada clave foránea.
- [x] Explicar que el índice de la PK `(turno_id, practica_id)` ya cubre búsquedas
      por `turno_id`, por ser su primera columna: no hace falta otro índice propio.
- [x] Adjuntar evidencia de consola para turnos con una y tres prácticas (C-07).
- [x] Verificar que no haya credenciales reales versionadas.
- [ ] Revisar el índice de Git, crear el commit y subir la entrega (acción del usuario).

Revisión final del 4 de noviembre de 2026: 72 pruebas aprobadas y `pip check` sin
conflictos. C-01 a C-06 comprobados en PostgreSQL mediante esquema aislado y rollback
externo; C-08 rechazado por CHECK (23514), con precio intacto; C-09 aprobado contra
el servidor real. Evidencias en `test/evidencia_c07.md`, `test/evidencia_c08.md`,
`test/evidencia_c09.md` y resumen en `test/revision_final.md`.

Git no tenía archivos rastreados: `.env` y `.venv/` están ignorados. El análisis de
archivos candidatos no encontró secretos confirmados; el único aviso era un valor
de ejemplo del proyecto anterior. No se agregó nada al índice ni se crearon commits.

Fuera de alcance: autenticación, autorización, repositorios, Unit of Work,
colas de tareas, Alembic y frontend.
