-- ============================================================================
-- DIAPOSITIVA 17 — EL GARANTE QUE NO DEPENDE DE QUIÉN ESCRIBE
-- Se corre en pgAdmin (Query Tool) o con psql, conectado a capitulo4_db.
-- Esquiva la API a propósito: es "un script que escribe directo a la base".
-- ============================================================================

-- 1) Las comprobaciones que guarda la tabla producto
-- Qué decir: no están en el código de Python; están en la base, con nombre propio.
-- Esperado: ck_producto_costo_no_negativo → CHECK ((costo_interno >= (0)::numeric))
--           ck_producto_precio_positivo   → CHECK ((precio > (0)::numeric))
SELECT conname AS restriccion, pg_get_constraintdef(oid) AS definicion
FROM pg_constraint
WHERE conrelid = 'producto'::regclass AND contype = 'c'
ORDER BY conname;

-- 2) Un precio negativo, directo en la base
-- Qué decir: nadie pasó por FastAPI ni por Pydantic. La base lo rechaza igual.
-- Esperado: ERROR: el nuevo registro para la relación «producto» viola la
--           restricción «check» «ck_producto_precio_positivo»
UPDATE producto SET precio = -5 WHERE id = 1;

-- 3) El costo interno no tiene DTO: la base es la única que lo protege
-- Esperado: ERROR ... «ck_producto_costo_no_negativo»
UPDATE producto SET costo_interno = -1 WHERE id = 1;

-- 4) Un cambio válido entra sin problemas
-- Esperado: UPDATE 1
UPDATE producto SET precio = 1300 WHERE id = 1;

-- Para volver al precio de las diapositivas: python reiniciar.py
