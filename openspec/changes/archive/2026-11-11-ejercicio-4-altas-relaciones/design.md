# Design: Ejercicio 4 - Altas con relaciones

## Approach
- **Libros**: El DTO `LibroCreate` ya incluye los campos necesarios. En `app/modules/libros/service.py`, al crear el libro, se instancian los objetos `LibroAutor` asociados. Si un `editorial_id`, `genero_id` o `autor_id` no existe, la base de datos lanzará un `IntegrityError` debido a la clave foránea, el cual es interceptado por el manejador global o centralizado de errores (`crud.py` o similar) para retornar un código 409 con mensaje propio (sin exponer detalles internos).
- **Ventas**: El DTO `VentaCreate` recibe `cliente_id` y `renglones`. En `app/modules/ventas/service.py`, se consultan los precios actuales de los libros involucrados en una sola consulta. Si alguno no existe, se rechaza. Se construyen los `RenglonVenta` copiando el precio unitario del libro, se calcula el `total` como la suma de `cantidad * precio_unitario`, se asigna la fecha actual con zona horaria y se persiste la venta con sus renglones en una transacción.

## Components Affected
- `app/modules/libros/service.py`
- `app/modules/ventas/service.py`
- `app/core/crud.py` (manejo de `IntegrityError` -> 409)
- `test/` (archivos `.http`)
