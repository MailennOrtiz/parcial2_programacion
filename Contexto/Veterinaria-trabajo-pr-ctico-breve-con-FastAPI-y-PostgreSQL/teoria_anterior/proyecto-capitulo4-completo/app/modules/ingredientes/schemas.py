from sqlmodel import SQLModel


class IngredienteCreate(SQLModel):
    # Sin id: lo asigna la base.
    nombre: str


class IngredienteRead(SQLModel):
    """La fila tal cual está guardada. No hay ninguna columna de productos."""

    id: int
    nombre: str


class ProductoQueLoLleva(SQLModel):
    """El muchos a muchos leído desde el otro extremo."""

    producto_id: int
    producto: str
    cantidad: int
