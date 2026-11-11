"""Producto y su receta.

Diapositiva 6 — muchos a muchos: la tabla intermedia es la receta.
Diapositiva 7 — agregación: el producto puede existir sin su categoría.
Diapositiva 17 — el CHECK: el garante que no depende de quién escribe.
Diapositiva 18 — la unicidad del nombre la impone la base, no el service.

Agregación al crear (archivo test/13 y la página /static/relaciones.html): en el DTO viaja el
id de una categoría que ya existe, y la vuelta la trae armada por `Producto.categoria`.
"""

from decimal import Decimal
from typing import TYPE_CHECKING

from sqlmodel import CheckConstraint, Field, Relationship, SQLModel

from app.modules.categorias.models import Categoria
from app.modules.ingredientes.models import Ingrediente

if TYPE_CHECKING:
    # Sólo para las anotaciones: evita el import circular en tiempo de ejecución
    # (pedidos/models.py también menciona a Producto).
    from app.modules.pedidos.models import DetallePedido


class Producto(SQLModel, table=True):
    """El producto: una fila que describe cómo es la cosa hoy.

    Diapositiva 17. Los dos CheckConstraint viven DENTRO de la base: los respeta cualquiera que
    escriba en esta tabla, sea la API, un script de carga o alguien conectado con psql. La
    validación del DTO (`gt=0` en ProductoCreate) sólo protege la puerta de la API: un
    `UPDATE producto SET precio = -5` hecho directo en la base la esquiva por completo. El CHECK
    no. Cada uno lleva un nombre explícito; si no, PostgreSQL les pone uno ilegible.
    """

    __table_args__ = (
        CheckConstraint("precio > 0", name="ck_producto_precio_positivo"),
        CheckConstraint("costo_interno >= 0", name="ck_producto_costo_no_negativo"),
    )

    id: int | None = Field(default=None, primary_key=True)

    # unique=True: diapositiva 18. Es la base la que rechaza el segundo producto con el mismo
    # nombre, no un "SELECT antes de INSERT" en el service, que no cierra la ventana entre
    # preguntar y escribir cuando dos peticiones llegan al mismo tiempo.
    nombre: str = Field(unique=True, index=True)

    # El dinero es Decimal y en la base NUMERIC(10,2), nunca float (Capítulo 2, sección 2.7).
    precio: Decimal = Field(max_digits=10, decimal_places=2)

    # Sólo vive en la tabla: no aparece en ningún DTO de entrada ni de salida. La API no lo
    # recibe ni lo expone, así que la única manera de garantizar que nunca sea negativo es el
    # CHECK de arriba.
    costo_interno: Decimal = Field(default=Decimal("0"), max_digits=10, decimal_places=2)

    categoria_id: int | None = Field(
        default=None, foreign_key="categoria.id", ondelete="RESTRICT"
    )

    categoria: Categoria | None = Relationship(back_populates="productos")

    ingredientes: list["ProductoIngrediente"] = Relationship(
        back_populates="producto", passive_deletes=True
    )

    detalles: list["DetallePedido"] = Relationship(
        back_populates="producto", passive_deletes=True
    )


class ProductoIngrediente(SQLModel, table=True):
    """La receta: la tabla del medio de un muchos a muchos (diapositiva 6).

    Tiene DOS claves foráneas, una hacia cada lado, y juntas forman su clave
    primaria (el mismo ingrediente no figura dos veces en el mismo producto).

    Y tiene algo propio para decir: `cantidad`, en gramos. Cuánta cebolla
    lleva la empanada no es un dato de la empanada ni de la cebolla: es un
    dato de la relación entre las dos.

    Vive en el módulo `productos` porque la receta se arma desde el producto;
    el módulo `ingredientes` la importa desde acá.
    """

    __tablename__ = "producto_ingrediente"

    producto_id: int = Field(foreign_key="producto.id", primary_key=True)
    ingrediente_id: int = Field(foreign_key="ingrediente.id", primary_key=True)
    cantidad: int  # gramos

    # ── Navegación: la fila de la receta conoce sus dos extremos ─────────────
    # Es un "objeto de asociación": la tabla del medio es una entidad con
    # nombre propio porque tiene algo para decir (`cantidad`). Por eso no se usa
    # `link_model` (el muchos a muchos "directo" de SQLModel, Producto ↔
    # Ingrediente sin pasar por la fila): esconde la tabla del medio y con ella
    # la cantidad. Para ir de un producto a sus ingredientes se pasa por acá:
    # `producto.ingredientes[i].ingrediente`.
    producto: Producto = Relationship(back_populates="ingredientes")
    ingrediente: Ingrediente = Relationship(back_populates="productos")
