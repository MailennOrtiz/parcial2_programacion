-- Solo lectura: ejecutar después de completar 04_turnos.http, desde una base
-- reiniciada al comienzo. Estas consultas comprueban resultados, no consumos de ids.

-- Esperado: 0. Las tres reservas rechazadas no dejaron turnos.
SELECT COUNT(*) AS turnos_rechazados_guardados
FROM turno
WHERE motivo IN ('C-04 práctica inexistente', 'Mascota inexistente', 'Práctica repetida');

-- Esperado: 1 turno y 2 filas intermedias (solo el turno inicial).
-- El turno válido de C-06 se creó y después se borró en C-05.
SELECT (SELECT COUNT(*) FROM turno) AS turnos,
       (SELECT COUNT(*) FROM turno_practica) AS practicas_reservadas;

-- Esperado: 0. La cascada no deja filas huérfanas.
SELECT COUNT(*) AS partes_sin_turno
FROM turno_practica AS tp
LEFT JOIN turno AS t ON t.id = tp.turno_id
WHERE t.id IS NULL;

-- Esperado: 4. Borrar turnos no borra prácticas del catálogo.
SELECT COUNT(*) AS practicas_del_catalogo FROM practica;
