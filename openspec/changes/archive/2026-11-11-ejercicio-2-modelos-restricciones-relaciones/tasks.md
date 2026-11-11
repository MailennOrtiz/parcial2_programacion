# Tasks

## 1. Modelos de tabla

- [x] 1.1 Implementar `Editorial` y `Genero` con `nombre` UNIQUE e índice.
- [x] 1.2 Implementar `Autor` con `id`, `nombre` y `nacionalidad`.
- [x] 1.3 Implementar `Libro` con ISBN UNIQUE, CHECK `precio > 0`, CHECK `stock >= 0`, FK a editorial (requerida) y género (opcional) indexadas.
- [x] 1.4 Implementar `LibroAutor` como entidad de asociación con PK compuesta, rol restringido y CHECK `orden >= 1`.
- [x] 1.5 Implementar `Cliente` con `email` UNIQUE e índice.
- [x] 1.6 Implementar `PerfilCliente` con `cliente_id` UNIQUE e índice (uno a uno).
- [x] 1.7 Implementar `Venta` con `cliente_id` indexado, `fecha` con zona horaria y CHECK `total >= 0`.
- [x] 1.8 Implementar `RenglonVenta` con `venta_id` y `libro_id` indexados, CHECK `cantidad > 0` y CHECK `precio_unitario > 0`.

## 2. Relaciones y navegación

- [x] 2.1 Declarar `Relationship(back_populates=...)` en ambos extremos de cada FK.
- [x] 2.2 Asegurar que `Cliente.perfil` devuelva un objeto (`uselist=False`).
- [x] 2.3 Representar el dinero con `Decimal` (`Numeric`).

## 3. Registro y verificación

- [x] 3.1 Importar todos los modelos en `app/core/modelos.py`.
- [x] 3.2 Verificar que `SQLModel.metadata` contenga las 9 tablas con columnas y restricciones esperadas.
- [x] 3.3 Verificar que las relaciones se configuren sin errores de importación.