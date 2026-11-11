# DTO del m�dulo clientes (se implementan en ejercicios posteriores).
"""Contratos de clientes y perfiles."""
from pydantic import EmailStr, field_validator
from sqlmodel import Field
from app.core.schemas import Entrada, Lectura

class ClienteCreate(Entrada):
    nombre: str = Field(min_length=1, max_length=200)
    email: EmailStr

class ClienteUpdate(Entrada):
    nombre: str | None = Field(default=None, min_length=1, max_length=200)
    email: EmailStr | None = None

    @field_validator("nombre", "email")
    @classmethod
    def campos_no_nulos(cls, valor):
        if valor is None:
            raise ValueError("El campo no puede ser null.")
        return valor

class PerfilCreate(Entrada):
    telefono: str = Field(min_length=1, max_length=40)
    direccion: str = Field(min_length=1, max_length=250)

class PerfilRead(Lectura):
    id: int
    cliente_id: int
    telefono: str
    direccion: str

class ClienteResumenRead(Lectura):
    id: int
    nombre: str
    email: EmailStr

class ClienteRead(ClienteResumenRead):
    perfil: PerfilRead | None
