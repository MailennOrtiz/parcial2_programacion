-- ============================================================================
-- DIAPOSITIVA 8 — LA CLAVE FORÁNEA SE INDEXA
-- «Las solapas de la libreta»: PostgreSQL no las pone solo
-- Se corre en pgAdmin (Query Tool) o con psql, conectado a capitulo4_db,
-- una sentencia por vez y en orden.
--
-- OJO: este archivo CAMBIA la base (agrega 60.000 pedidos y un índice). Para
-- volver a los datos de las diapositivas, corré python reiniciar.py.
-- ============================================================================

-- 1) Se agranda la tabla pedido: 2.000 usuarios y 60.000 pedidos más
-- Qué decir: con tres pedidos no se nota nada. Con sesenta mil, sí.
-- Los usuarios nuevos empiezan en el id 1000 y los pedidos se reparten entre
-- ellos: los de Marta (usuario 7) siguen siendo sólo el 101 y el 102.
INSERT INTO usuario (id, nombre)
SELECT n, 'Cliente ' || n FROM generate_series(1000, 2999) AS n;

INSERT INTO pedido (id, usuario_id)
SELECT 1000 + n, 1000 + (n % 2000) FROM generate_series(1, 60000) AS n;

-- ANALYZE actualiza las estadísticas con las que la base elige cómo buscar.
ANALYZE pedido;

-- Esperado: 60003 pedidos en total, 2 de Marta
SELECT count(*) AS pedidos_en_la_tabla,
       count(*) FILTER (WHERE usuario_id = 7) AS pedidos_de_marta
FROM pedido;

-- 2) ¿Qué índices tiene la tabla pedido? Se le pregunta a la base
-- Qué decir: sólo el de la clave primaria. Declarar la clave foránea NO creó
-- un índice.
-- Esperado: sólo pedido_pkey
SELECT indexname AS indice, indexdef AS definicion
FROM pg_indexes
WHERE tablename = 'pedido';

-- 3) SIN índice: cómo busca la base los pedidos de Marta
-- Qué decir: Seq Scan = pasar hoja por hoja. Miren «Rows Removed by Filter»:
-- son las filas que miró y descartó.
-- Esperado: Seq Scan on pedido · Rows Removed by Filter: 60001
EXPLAIN ANALYZE SELECT id FROM pedido WHERE usuario_id = 7;

-- 4) Se le ponen las solapas a la libreta
-- Qué decir: en el modelo sería Field(foreign_key="usuario.id", index=True)
-- (pedidos/models.py, que a propósito no lo tiene).
CREATE INDEX ix_pedido_usuario_id ON pedido (usuario_id);

ANALYZE pedido;

-- Esperado: pedido_pkey e ix_pedido_usuario_id
SELECT indexname AS indice, indexdef AS definicion
FROM pg_indexes
WHERE tablename = 'pedido';

-- 5) CON índice: la misma consulta
-- Qué decir: los tiempos cambian de una corrida a otra; lo que no cambia es
-- la forma de buscar ni las filas que tuvo que mirar.
-- Esperado: usa ix_pedido_usuario_id · ya no aparece «Rows Removed by Filter»
EXPLAIN ANALYZE SELECT id FROM pedido WHERE usuario_id = 7;

-- 6) (Opcional) Sacar el índice para repetir la comparación desde el paso 3
-- Qué decir: cada índice tiene un costo: hace más lentas las escrituras.
DROP INDEX ix_pedido_usuario_id;
