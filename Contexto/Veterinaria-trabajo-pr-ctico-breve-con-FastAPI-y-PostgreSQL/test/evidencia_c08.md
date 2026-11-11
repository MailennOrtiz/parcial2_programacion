# Evidencia C-08 — CHECK de precio en PostgreSQL

Comprobación realizada el 4 de noviembre de 2026 sobre PostgreSQL **18.4**.
La escritura se ejecutó directamente mediante una conexión SQLAlchemy/asyncpg,
sin pasar por FastAPI ni sus DTO. Se usó la base configurada en el entorno,
sin mostrar sus credenciales.

## Escritura probada

```sql
UPDATE practica SET precio = 0 WHERE id = 1;
```

El precio de esa práctica antes de la prueba era `15000.00`.

## Resultado real

Fragmento de la salida de la comprobación:

```text
2026-11-04 15:39:08,600 INFO sqlalchemy.engine.Engine UPDATE practica SET precio = 0 WHERE id = 1
2026-11-04 15:39:08,600 INFO sqlalchemy.engine.Engine [generated in 0.00018s] ()
C-08 rechazo: SQLSTATE=23514, restriccion=ck_practica_precio_positivo
2026-11-04 15:39:08,641 INFO sqlalchemy.engine.Engine ROLLBACK
```

El controlador produjo un `IntegrityError`. Se comprobaron su SQLSTATE (`23514`,
violación de CHECK) y el nombre de la restricción rechazante. La transacción se
deshizo incluso ante errores; no se confirmó ninguna escritura.

Verificación posterior:

```text
PostgreSQL: 18.4
Precio inicial: 15000.00; precio final: 15000.00
C-08 APROBADO. Se ejecuto ROLLBACK; no se modificaron datos persistidos.
```

## Conclusión

PostgreSQL garantiza `precio > 0` aunque la escritura no pase por el contrato de
entrada. El UPDATE inválido fue rechazado y el precio original permaneció intacto.
El archivo `07_check.sql` permite repetir la prueba por bloques desde pgAdmin.
