# Tasks: Ejercicio 5 - Lecturas sin N+1

## 1. Auditoría de cargas anticipadas

- [x] 1.1 Revisar `app/modules/libros/service.py`: confirmar `opciones()` con `joinedload` editorial/género + `selectinload` autorías→autor + `raiseload("*")`; verificar `listar` y `obtener` usan `opciones()`.
- [x] 1.2 Revisar `app/modules/ventas/service.py`: confirmar `opciones()` con `joinedload` cliente + `selectinload` renglones→libro + `raiseload("*")`.
- [x] 1.3 Revisar `app/modules/clientes/service.py`, `autores/service.py`, `editoriales/service.py`, `generos/service.py`: documentar invariantes (crud solo para entidades sin relaciones en respuesta).

## 2. Eliminación de accesos perezosos en serialización

- [x] 2.1 Convertir `libros/listar` para construir `LibroResumenRead` en el servicio (o en el router) en lugar de devolver ORM crudo; verificar `test_libros_autores_filtrado_y_fk` sigue pasando.
- [x] 2.2 Convertir `autores/libros` para construir `LibroDeAutorRead` en el servicio; verificar respuesta y conteo de consultas.
- [x] 2.3 Asegurar `clientes/obtener` y `clientes/crear_perfil` no disparen carga perezosa al serializar `ClienteRead`/`PerfilRead`; verificar `test_clientes_perfil_y_venta`.

## 3. Prueba C-07 (conteo de consultas)

- [x] 3.1 Implementar listener de SQLAlchemy en `test/test_n_plus_1.py` que cuente `SELECT` por caso.
- [x] 3.2 Caso libro: crear libro con 1 autor y con N autores; afirmar conteo idéntico para `GET /libros/{id}`.
- [x] 3.3 Caso venta: crear venta con 1 renglón y con N renglones; afirmar conteo idéntico para `GET /ventas/{id}`.
- [x] 3.4 Verificar que no aparecen `InvalidRequestError`/carga perezosa.

## 4. Documentación manual y verificación final

- [x] 4.1 Crear `test/05_lecturas_n_plus_1.http` con casos C-07 y guía `SQL_ECHO`.
- [x] 4.2 Ejecutar suite completa (`python -m unittest discover -s test -p "test_*.py" -v`) y confirmar verde.
- [x] 4.3 Validar change con `openspec validate ejercicio-5-lecturas-sin-n-plus-1`.