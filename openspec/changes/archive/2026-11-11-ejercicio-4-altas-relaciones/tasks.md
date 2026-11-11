# Tasks: Ejercicio 4 - Altas con relaciones

- [x] 1. Verificar el manejo de IntegrityError en `app/core/crud.py` para asegurar que las violaciones de claves foráneas y restricciones devuelvan 409 con mensaje propio. <!-- id: 1 -->
- [x] 2. Revisar y ajustar el servicio de libros (`app/modules/libros/service.py`) para garantizar el alta con agregación y muchos a muchos sin validaciones previas con `if` (delegando en la base de datos). <!-- id: 2 -->
- [x] 3. Revisar y ajustar el servicio de ventas (`app/modules/ventas/service.py`) para cumplir con RN-04 a RN-07 (copiar precios de los libros, calcular el total, manejar la composición con renglones). <!-- id: 3 -->
- [x] 4. Verificar y documentar los casos de prueba `.http` para C-04, C-05 y C-06. <!-- id: 4 -->
