-- C-08: PostgreSQL rechaza precio=0 incluso sin pasar por FastAPI ni sus DTO.
-- Abrir Query Tool de pgAdmin conectado a la base del TP.
-- Ejecutar CADA BLOQUE seleccionado por separado, en esta misma conexión.
-- Después del error esperado, ejecutar ROLLBACK antes de cualquier otra consulta.
-- Si la práctica 1 no existe, cargar primero los datos iniciales del TP.

-- 1. Anotar el precio inicial (debe existir una fila; con el seed: 15000.00).
SELECT id, nombre, precio FROM practica WHERE id = 1;

-- 2. Abrir la transacción.
BEGIN;

-- 3. Ejecutar solo este UPDATE.
-- Esperado: ERROR, SQLSTATE 23514, restricción ck_practica_precio_positivo.
-- Aunque por error no existiera el CHECK, el ROLLBACK siguiente revierte el cambio.
UPDATE practica SET precio = 0 WHERE id = 1;

-- 4. Ejecutar SIEMPRE, también después del error. No ejecutar COMMIT.
ROLLBACK;

-- 5. El precio debe ser igual al observado en el paso 1.
SELECT id, nombre, precio FROM practica WHERE id = 1;
