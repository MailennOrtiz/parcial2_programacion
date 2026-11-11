# Evidencia C-07 — Lectura de turnos sin N+1

## Objetivo

Comprobar que el detalle de un turno con una práctica y el de un turno con tres
prácticas se resuelven con la misma cantidad de consultas SELECT.

## Estado de la evidencia

Las respuestas HTTP siguientes se transcribieron de las capturas obtenidas el
4 de noviembre de 2026. Ambos detalles respondieron 200 y devolvieron las
prácticas esperadas. Los fragmentos de consola se transcribieron de la captura
adicional del mismo día, que muestra ambos GET ejecutados nuevamente a las
14:55:30 y 14:55:35 (hora local del registro). Las cabeceras HTTP anteriores
corresponden a las primeras lecturas y expresan la hora en GMT.

**Evidencia completa: se observan dos SELECT por detalle en ambos casos.**

## Caso A — Turno con una práctica

Petición:

```http
GET http://127.0.0.1:8000/turnos/2
```

Respuesta observada:

```http
HTTP/1.1 200 OK
date: Wed, 04 Nov 2026 17:53:12 GMT
content-type: application/json
```

```json
{
  "id": 2,
  "fecha": "2026-11-13T13:30:00Z",
  "motivo": "C-07 una práctica",
  "total": "15000.00",
  "mascota": {
    "id": 1,
    "nombre": "Toby",
    "especie": "perro"
  },
  "practicas": [
    {
      "practica_id": 1,
      "nombre": "Consulta",
      "precio_unitario": "15000.00"
    }
  ]
}
```

### Consola SQL del caso A

Transcripción del fragmento de la terminal; los saltos debidos al ancho de la
captura se unificaron sin modificar el contenido SQL:

```text
2026-11-04 14:55:30,792 INFO sqlalchemy.engine.Engine BEGIN (implicit)
2026-11-04 14:55:30,792 INFO sqlalchemy.engine.Engine SELECT turno.id, turno.mascota_id, turno.fecha, turno.motivo, turno.total, mascota_1.id AS id_1, mascota_1.nombre, mascota_1.especie, mascota_1.duenio_id
FROM turno LEFT OUTER JOIN mascota AS mascota_1 ON mascota_1.id = turno.mascota_id
WHERE turno.id = $1::INTEGER
2026-11-04 14:55:30,793 INFO sqlalchemy.engine.Engine [cached since 498.9s ago] (2,)
2026-11-04 14:55:30,794 INFO sqlalchemy.engine.Engine SELECT turno_practica.turno_id, turno_practica.practica_id, turno_practica.precio_unitario, practica_1.id, practica_1.nombre, practica_1.precio
FROM turno_practica LEFT OUTER JOIN practica AS practica_1 ON practica_1.id = turno_practica.practica_id
WHERE turno_practica.turno_id IN ($1::INTEGER)
2026-11-04 14:55:30,794 INFO sqlalchemy.engine.Engine [cached since 498.9s ago] (2,)
INFO:     127.0.0.1:65392 - "GET /turnos/2 HTTP/1.1" 200 OK
2026-11-04 14:55:30,796 INFO sqlalchemy.engine.Engine ROLLBACK
```

**Conteo: 2 SELECT.** Ambos reciben el id 2 como parámetro.

## Caso B — Turno con tres prácticas

Petición:

```http
GET http://127.0.0.1:8000/turnos/3
```

Respuesta observada:

```http
HTTP/1.1 200 OK
date: Wed, 04 Nov 2026 17:53:21 GMT
content-type: application/json
```

```json
{
  "id": 3,
  "fecha": "2026-11-13T14:30:00Z",
  "motivo": "C-07 tres prácticas",
  "total": "35000.00",
  "mascota": {
    "id": 1,
    "nombre": "Toby",
    "especie": "perro"
  },
  "practicas": [
    {
      "practica_id": 1,
      "nombre": "Consulta",
      "precio_unitario": "15000.00"
    },
    {
      "practica_id": 2,
      "nombre": "Desparasitación",
      "precio_unitario": "8000.00"
    },
    {
      "practica_id": 3,
      "nombre": "Vacuna antirrábica",
      "precio_unitario": "12000.00"
    }
  ]
}
```

### Consola SQL del caso B

Transcripción del segundo fragmento completo de la terminal:

```text
2026-11-04 14:55:35,060 INFO sqlalchemy.engine.Engine BEGIN (implicit)
2026-11-04 14:55:35,060 INFO sqlalchemy.engine.Engine SELECT turno.id, turno.mascota_id, turno.fecha, turno.motivo, turno.total, mascota_1.id AS id_1, mascota_1.nombre, mascota_1.especie, mascota_1.duenio_id
FROM turno LEFT OUTER JOIN mascota AS mascota_1 ON mascota_1.id = turno.mascota_id
WHERE turno.id = $1::INTEGER
2026-11-04 14:55:35,060 INFO sqlalchemy.engine.Engine [cached since 503.2s ago] (3,)
2026-11-04 14:55:35,062 INFO sqlalchemy.engine.Engine SELECT turno_practica.turno_id, turno_practica.practica_id, turno_practica.precio_unitario, practica_1.id, practica_1.nombre, practica_1.precio
FROM turno_practica LEFT OUTER JOIN practica AS practica_1 ON practica_1.id = turno_practica.practica_id
WHERE turno_practica.turno_id IN ($1::INTEGER)
2026-11-04 14:55:35,062 INFO sqlalchemy.engine.Engine [cached since 503.2s ago] (3,)
INFO:     127.0.0.1:65393 - "GET /turnos/3 HTTP/1.1" 200 OK
2026-11-04 14:55:35,064 INFO sqlalchemy.engine.Engine ROLLBACK
```

**Conteo: 2 SELECT.** Ambos reciben el id 3 como parámetro.

## Comparación

| Caso | Turno | Prácticas devueltas | Estado HTTP | SELECT observados en consola |
| --- | --- | --- | --- | --- |
| A | 2 | 1 | 200 | 2 |
| B | 3 | 3 | 200 | 2 |

Las consultas observadas corresponden a la estrategia de precarga de la implementación:

1. Turno y mascota mediante `joinedload(Turno.mascota)`.
2. Sus partes mediante `selectinload(Turno.practicas)`, junto con la práctica
   de catálogo mediante `joinedload(TurnoPractica.practica)`.

`BEGIN`, `COMMIT` y `ROLLBACK` no se cuentan como SELECT. Las líneas de parámetros
tampoco son consultas adicionales. La marca `[cached since ...]` indica reutilización
de la compilación SQL, no que se haya evitado ejecutar la consulta.

El `ROLLBACK` al cerrar la sesión de estas peticiones de lectura finaliza la
transacción implícita: no indica que haya fallado el GET. Ambos devolvieron 200.
La petición a `/health` que aparece entre otros registros de la captura es ajena
a C-07 y no se incluyó en los fragmentos analizados.

## Conclusión

Ambos detalles ejecutan dos consultas SELECT y devuelven correctamente una y tres
prácticas, respectivamente. Aumentar de una a tres prácticas no aumenta la cantidad
de consultas: la colección se carga en conjunto, no mediante una consulta por parte.
La ejecución observada demuestra el comportamiento sin N+1 solicitado en C-07.
