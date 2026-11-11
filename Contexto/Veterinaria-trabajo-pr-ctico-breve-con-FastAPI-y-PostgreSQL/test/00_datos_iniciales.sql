-- Ejecutar sobre la base de veterinaria después de python reiniciar.py.
-- Solo lectura. Esperado: 2, 1, 3, 4, 1 y 2 filas, respectivamente.
SELECT 'duenio' AS tabla, COUNT(*) AS filas FROM duenio
UNION ALL SELECT 'ficha_duenio', COUNT(*) FROM ficha_duenio
UNION ALL SELECT 'mascota', COUNT(*) FROM mascota
UNION ALL SELECT 'practica', COUNT(*) FROM practica
UNION ALL SELECT 'turno', COUNT(*) FROM turno
UNION ALL SELECT 'turno_practica', COUNT(*) FROM turno_practica;

-- Turno inicial: Toby, Control anual, total 27000.00.
-- Dos filas: Consulta a 15000.00 y Vacuna antirrábica a 12000.00.
SELECT t.id, m.nombre AS mascota, t.fecha, t.motivo, t.total,
       p.nombre AS practica, tp.precio_unitario
FROM turno AS t
JOIN mascota AS m ON m.id = t.mascota_id
JOIN turno_practica AS tp ON tp.turno_id = t.id
JOIN practica AS p ON p.id = tp.practica_id
ORDER BY t.id, tp.practica_id;
