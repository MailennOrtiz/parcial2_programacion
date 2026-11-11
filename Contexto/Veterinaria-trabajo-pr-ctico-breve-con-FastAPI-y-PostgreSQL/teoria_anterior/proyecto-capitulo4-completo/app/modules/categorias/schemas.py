from sqlmodel import SQLModel


class CategoriaCreate(SQLModel):
    # Sin id: lo asigna la base. El DTO trae sólo lo que el cliente sabe.
    nombre: str


class CategoriaRead(SQLModel):
    id: int
    nombre: str
