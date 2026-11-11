-- ============================================================================
-- CÓMO QUEDÓ ARMADA LA BASE (diapositivas 4 a 7)
-- Se corre en pgAdmin (Query Tool) o con psql, conectado a capitulo4_db.
-- Son sólo consultas: no cambian nada. Se pueden correr una por una.
--
-- La idea: no mirar lo que dice el modelo de Python, sino preguntarle A LA
-- BASE qué tiene guardado.
-- ============================================================================

-- ── DIAPOSITIVA 4 · La clave foránea ────────────────────────────────────────
-- Qué decir: no es una convención del programa; es una restricción que la
-- base guarda.
-- Esperado: pedido_usuario_id_fkey → FOREIGN KEY (usuario_id) REFERENCES usuario(id)
SELECT conname AS restriccion, pg_get_constraintdef(oid) AS definicion
FROM pg_constraint
WHERE conrelid = 'pedido'::regclass
ORDER BY contype, conname;

-- ── DIAPOSITIVA 4 · Uno a muchos ────────────────────────────────────────────
-- Qué decir: en el diagrama de clases el usuario «tiene» una lista de pedidos.
-- En la tabla no hay dónde ponerla: una columna guarda un valor, no una lista.
-- Esperado: usuario → sólo id y nombre. Ninguna columna de pedidos.
SELECT column_name AS columna, data_type AS tipo
FROM information_schema.columns
WHERE table_name = 'usuario'
ORDER BY ordinal_position;

-- Qué decir: la relación está anotada acá, del lado «muchos».
-- Esperado: pedido → id y usuario_id
SELECT column_name AS columna, data_type AS tipo
FROM information_schema.columns
WHERE table_name = 'pedido'
ORDER BY ordinal_position;

-- ── DIAPOSITIVA 5 · Uno a uno ───────────────────────────────────────────────
-- Qué decir: las dos tablas difieren en una palabra del modelo (unique=True).
-- Esperado: perfil tiene clave foránea (perfil_usuario_id_fkey) Y unicidad
-- (perfil_usuario_id_key); perfil_sin_unicidad tiene sólo la clave foránea.
SELECT conrelid::regclass AS tabla, conname AS restriccion,
       pg_get_constraintdef(oid) AS definicion
FROM pg_constraint
WHERE conrelid IN ('perfil'::regclass, 'perfil_sin_unicidad'::regclass)
  AND contype IN ('f', 'u')
ORDER BY 1, contype, conname;

-- ── DIAPOSITIVA 6 · Muchos a muchos ─────────────────────────────────────────
-- Qué decir: ni producto ni ingrediente tienen dónde anotar al otro.
-- Esperado: ingrediente → id, nombre · producto → id, nombre, precio, costo_interno, categoria_id
SELECT table_name AS tabla, column_name AS columna
FROM information_schema.columns
WHERE table_name IN ('producto', 'ingrediente')
ORDER BY table_name, ordinal_position;

-- Qué decir: la tabla del medio tiene dos claves foráneas, una hacia cada
-- lado, y las dos juntas son su clave primaria.
-- Esperado: dos FOREIGN KEY y PRIMARY KEY (producto_id, ingrediente_id)
SELECT conname AS restriccion, pg_get_constraintdef(oid) AS definicion
FROM pg_constraint
WHERE conrelid = 'producto_ingrediente'::regclass
ORDER BY contype, conname;

-- ── DIAPOSITIVA 7 · Agregación y composición ────────────────────────────────
-- Qué decir: las dos relaciones llevan clave foránea. Miren el final de cada
-- definición: ahí está la diferencia.
-- Esperado: detalle_pedido_pedido_id_fkey → ... ON DELETE CASCADE
--           producto_categoria_id_fkey    → ... ON DELETE RESTRICT
SELECT conrelid::regclass AS tabla, conname AS restriccion,
       pg_get_constraintdef(oid) AS definicion
FROM pg_constraint
WHERE conname IN ('detalle_pedido_pedido_id_fkey', 'producto_categoria_id_fkey')
ORDER BY 1;
