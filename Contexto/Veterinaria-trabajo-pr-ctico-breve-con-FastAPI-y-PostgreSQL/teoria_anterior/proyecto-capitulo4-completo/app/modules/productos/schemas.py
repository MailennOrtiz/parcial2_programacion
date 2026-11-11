from decimal import Decimal

from sqlmodel import Field, SQLModel

from app.modules.categorias.schemas import CategoriaRead


# ─── Producto ──────────────────────────────────────────────────────────────
class ProductoCreate(SQLModel):
    """Lo que trae un alta. Ni `id` ni `costo_interno`: si vinieran, no se usan."""

    nombre: str = Field(min_length=1)
    # gt=0 protege la puerta de la API. El CHECK de la tabla protege la base (diapositiva 17).
    precio: Decimal = Field(gt=0, max_digits=10, decimal_places=2)
    # Agregación: viaja el id de una categoría que YA existe. La categoría no
    # se crea ni se modifica: se la nombra. Puede no venir (None): en la
    # agregación la parte puede existir sin el todo.
    categoria_id: int | None = None


class ProductoRead(SQLModel):
    """La fila tal cual está guardada, sin `costo_interno`. No hay ninguna columna de ingredientes."""

    id: int
    nombre: str
    precio: Decimal
    categoria_id: int | None = None


class ProductoConCategoriaRead(ProductoRead):
    """La vuelta de POST /productos/: el producto y su categoría, armada.

    `categoria_id` es lo que se guardó; `categoria`, la fila a la que apunta.
    """

    categoria: CategoriaRead | None = None


# ─── La receta (muchos a muchos) ───────────────────────────────────────────
class RecetaCreate(SQLModel):
    ingrediente_id: int
    cantidad: int  # gramos


class RecetaFila(SQLModel):
    """Una fila de la tabla intermedia, tal cual está guardada."""

    producto_id: int
    ingrediente_id: int
    cantidad: int


class IngredienteDeLaReceta(SQLModel):
    """La receta con nombres: la tabla intermedia unida con ingrediente."""

    ingrediente_id: int
    ingrediente: str
    cantidad: int
