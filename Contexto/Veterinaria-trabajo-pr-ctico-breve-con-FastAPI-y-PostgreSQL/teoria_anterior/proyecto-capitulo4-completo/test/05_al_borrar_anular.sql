-- ============================================================================
-- DIAPOSITIVA 7 — ANULAR: la misma clave foránea, con otra respuesta
-- Se corre en pgAdmin (Query Tool) o con psql, conectado a capitulo4_db,
-- DESPUÉS del paso 6 de 05_al_borrar.http (el borrado de Comidas rechazado).
--
-- OJO: este archivo CAMBIA la base. Para volver a como estaba, corré
-- python reiniciar.py: recrea el esquema con la regla RESTRICT.
-- ============================================================================

-- 1) Cómo está hoy la clave foránea de producto.categoria_id
-- Esperado: ... ON DELETE RESTRICT
SELECT pg_get_constraintdef(oid) AS definicion
FROM pg_constraint
WHERE conname = 'producto_categoria_id_fkey';

-- 2) Se cambia la decisión: de RESTRICT a SET NULL
-- Qué decir: es la MISMA clave foránea con una palabra distinta. En el modelo
-- sería ondelete="SET NULL" en Producto.categoria_id (productos/models.py).
ALTER TABLE producto DROP CONSTRAINT producto_categoria_id_fkey;

ALTER TABLE producto ADD CONSTRAINT producto_categoria_id_fkey
    FOREIGN KEY (categoria_id) REFERENCES categoria (id) ON DELETE SET NULL;

-- 3) Cómo quedó
-- Esperado: ... ON DELETE SET NULL
SELECT pg_get_constraintdef(oid) AS definicion
FROM pg_constraint
WHERE conname = 'producto_categoria_id_fkey';

-- Ahora volvé a 05_al_borrar.http y seguí desde el paso 7: el mismo
-- DELETE /categorias/1 que antes dio 409 ahora da 204, y la Empanada queda
-- con categoria_id vacío. El código no cambió: cambió la base.
