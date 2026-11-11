# Design

## Context

El ejercicio 2 del parcial traduce el modelo de dominio de la librería (Figura 1 y tablas de la consigna) a modelos de tabla SQLModel. La base es PostgreSQL 16 y el esquema se crea con `create_all` al arrancar. Los modelos viven en `app/modules/<modulo>/models.py` y se registran en `app/core/modelos.py`.

## Goals / Non-Goals

**Goals:**
- Implementar todas las tablas con las columnas, restricciones e índices obligatorios.
- Declarar la navegación en ambos extremos de cada relación.
- Mantener el dinero en `Decimal`.
- Garantizar que `Cliente.perfil` devuelva un objeto.

**Non-Goals:**
- No se implementan DTO ni endpoints (ejercicio 3).
- No se configuran ondelete específicos más allá de los implícitos; las reglas de borrado se refinan si hace falta.
- No se agregan migraciones.

## Decisions

- **SQLModel con `table=True`**: unifica modelo de tabla y validación; las restricciones se expresan con `Field` y `__table_args__`.
- **Claves foráneas con `index=True`**: PostgreSQL no crea índices automáticamente para FK.
- **Relaciones con `back_populates`**: navegación bidireccional explícita; `uselist=False` para el 1‑a‑1.
- **`TYPE_CHECKING` para referencias cruzadas**: evita imports circulares entre módulos; las referencias se resuelven al importar todos los modelos en `app/core/modelos.py`.
- **`Decimal` con `max_digits`/`decimal_places`**: mapea a `NUMERIC` de PostgreSQL.
- **`fecha` con `Column(DateTime(timezone=True))`**: garantiza zona horaria.
- **Entidad de asociación `LibroAutor`**: modela rol y orden propios de la relación muchos‑a‑muchos.

## Risks / Trade-offs

- [Riesgo] Las relaciones con referencias en string sólo se resuelven si se importan todos los modelos. → Mitigación: importar todos en `app/core/modelos.py` antes de `create_all`.
- [Riesgo] `create_all` no altera tablas existentes. → Mitigación: recrear la base en desarrollo; migraciones fuera de alcance.

## Migration Plan

No aplica. El esquema se crea automáticamente al arrancar sobre una base vacía.