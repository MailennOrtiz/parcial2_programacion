# Tasks

## 1. Contratos y servicios

- [x] 1.1 Definir DTO de creación, actualización y lectura para los recursos y relaciones requeridas.
- [x] 1.2 Implementar operaciones con sesión asincrónica, PATCH parcial y errores 404/409 propios.
- [x] 1.3 Implementar paginación y búsqueda de libros parametrizada.
- [x] 1.4 Precargar las relaciones incluidas en las respuestas.

## 2. Rutas

- [x] 2.1 Implementar y registrar los routers de editoriales, géneros, autores, libros, clientes y ventas.
- [x] 2.2 Comprobar códigos HTTP, validaciones y ausencia de PATCH de ventas.

## 3. Verificación

- [x] 3.1 Agregar pruebas de contratos, paginación, búsqueda, errores y actualizaciones parciales.
- [x] 3.2 Ejecutar las pruebas disponibles y registrar cualquier limitación de entorno.

## Limitación de la verificación

Las cuatro pruebas HTTP automatizadas pasaron con SQLite en memoria y claves
foráneas activas. No se ejecutaron los casos contra PostgreSQL: queda pendiente
verificar allí las restricciones, los conflictos de integridad, los PATCH y la
búsqueda. La aprobación de SQLite no sustituye esa validación ni las evidencias
exigidas por la consigna. Se archiva el cambio con esta limitación por decisión
explícita del usuario.
