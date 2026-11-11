# Casos de prueba

## Disponibles

- `00_health.http`: chequeos manuales de vida y disponibilidad de la base.
- `test_health.py`: nueve pruebas automatizadas de configuración, ciclo de vida,
  sesiones y salud. No requieren PostgreSQL y no verifican una conexión real.
- `test_modelos.py`: diez pruebas de tablas, restricciones, relaciones, índices,
  precisión monetaria y generación de SQL para PostgreSQL. No crean tablas ni
  ejecutan escrituras: los casos de integridad con datos reales siguen pendientes.
- `test_reiniciar.py`: siete pruebas de carga inicial sobre SQLite en memoria y
  flujo de reinicio con dobles de prueba. No acceden a la base configurada en `.env`.
- `00_datos_iniciales.sql`: consultas de solo lectura para comprobar cantidades,
  relaciones, precios y total del turno inicial en PostgreSQL después del reinicio.
- `test_crud.py`: 19 pruebas HTTP de los routers de dueños, fichas, prácticas y
  mascotas sobre SQLite asincrónico en memoria. Verifican códigos HTTP, contratos,
  rollback, precarga y paginación sin leer el `.env` ni acceder al PostgreSQL real.
- `01_duenios.http`: C-01, C-02 (email), C-03 y C-05 (dueño), además de PATCH,
  alta de ficha y borrado 204 sin cuerpo.
- `02_mascotas.http`: C-04 (dueño inexistente), altas, detalle y paginación.
- `03_practicas.http`: C-02 (nombre), catálogo y validación de importes.
- `test_turnos.py`: 19 pruebas de reserva todo o nada, contratos anidados, precios
  históricos, borrado en la base y detalle con dos SELECT para una y tres prácticas.
- `soporte_api.py`: entorno compartido de pruebas HTTP con base nueva en memoria.
- `04_turnos.http`: C-04 (práctica inexistente), C-05 (turno), C-06, lista vacía,
  práctica repetida y prohibición de importes enviados por el cliente.
- `04_turnos_verificar.sql`: verificación de rollback, cascada y catálogo conservado.
- `05_turnos_precarga.http`: prepara C-07 para capturar los dos SELECT de cada GET.
- `evidencia_c07.md`: respuestas HTTP y transcripción de consola aportadas por el
  usuario; verifica dos SELECT tanto con una práctica como con tres en PostgreSQL.
- `test_laboratorio.py`: ocho pruebas de stock, uso de hilos, concurrencia con barrera,
  handlers asincrónicos y script C-09. No necesitan base de datos.
- `06_laboratorio.http`: stock y salud. No hace falta reiniciar la base.
- `c09_concurrencia.py`: tres consultas simultáneas de stock y una de salud contra
  el servidor real; exige que salud responda mientras las tres consultas siguen pendientes.
- `07_check.sql`: C-08, UPDATE directo rechazado por el CHECK; ejecutar los bloques
  por separado y hacer siempre ROLLBACK, sin confirmar escrituras.
- `07_check.http`: validación complementaria del DTO (422), no reemplaza el SQL.
- `evidencia_c08.md`: rechazo real con SQLSTATE 23514 y precio original intacto.
- `evidencia_c09.md`: salida real del script contra Uvicorn, salud 200 en 0,005 s.
- `revision_final.md`: resumen de pruebas, regresión PostgreSQL y revisión de Git.

Desde la raíz:

```powershell
.\.venv\Scripts\python.exe -m pip install -r requirements-dev.txt
.\.venv\Scripts\python.exe -m unittest discover -s test -p "test_*.py" -v
```

## Estado de verificación

C-01 a C-06 fueron comprobados con los routers reales y PostgreSQL en un esquema
aislado dentro de una transacción externa, sin modificar los datos originales.
C-07 tiene evidencia de consola; C-08 tiene el rechazo real del CHECK; C-09 tiene
salida HTTP contra Uvicorn. Las 72 pruebas automatizadas también están aprobadas.
Ver `revision_final.md` y los tres archivos `evidencia_c*.md`.

## Concurrencia contra el servidor real

Iniciá Uvicorn con un solo worker y ejecutá desde otra terminal:

```powershell
.\.venv\Scripts\python.exe test/c09_concurrencia.py
```

No requiere reinicio ni acceso a PostgreSQL. El resultado esperado es salud 200
en menos de 0.5 segundos, con tres consultas de stock aún pendientes, y luego
stock 200 para las tres. El script devuelve código 1 si no lo demuestra.
La ejecución contra el servidor real del usuario ya se comprobó; la salida está
en `evidencia_c09.md`. Las pruebas automatizadas del script usan ASGI aislado.

Los `.http` se ejecutan sobre una base dedicada al TP después de `python reiniciar.py`
(borra datos), en orden dentro de cada archivo. Las referencias al id del dueño
en `01_duenios.http` usan la respuesta de la petición nombrada `nuevoDuenio` de
REST Client de VS Code; los archivos de turnos usan el mismo mecanismo. Las altas
rechazadas pueden consumir ids en PostgreSQL, así que no se suponen ids consecutivos.
El caso C-09 requiere peticiones simultáneas, no una
secuencia de llamadas individuales.
