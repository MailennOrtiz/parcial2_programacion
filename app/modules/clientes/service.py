# L�gica del m�dulo clientes (se implementa en ejercicios posteriores).
"""Operaciones de clientes y perfiles."""
from fastapi import HTTPException
from sqlalchemy.orm import joinedload, raiseload
from sqlmodel import select
from app.core import crud
from app.modules.clientes.models import Cliente, PerfilCliente

async def obtener(session, identificador):
    consulta = (select(Cliente).where(Cliente.id == identificador)
        .options(joinedload(Cliente.perfil), raiseload("*"))
        .execution_options(populate_existing=True))
    cliente = (await session.exec(consulta)).first()
    if cliente is None:
        raise HTTPException(status_code=404, detail="Cliente no encontrado.")
    return cliente

async def listar(session, limit, offset):
    consulta = (select(Cliente)
        .options(joinedload(Cliente.perfil), raiseload("*"))
        .order_by(Cliente.id)
        .limit(limit).offset(offset))
    return (await session.exec(consulta)).all()

async def crear(session, datos):
    cliente = Cliente.model_validate(datos)
    await crud.guardar(session, cliente)
    return await obtener(session, cliente.id)

async def actualizar(session, identificador, datos):
    cliente = await obtener(session, identificador)
    cliente.sqlmodel_update(datos.model_dump(exclude_unset=True))
    await crud.guardar(session, cliente)
    return await obtener(session, identificador)

async def crear_perfil(session, identificador, datos):
    await obtener(session, identificador)
    perfil = PerfilCliente(cliente_id=identificador, **datos.model_dump())
    await crud.guardar(session, perfil)
    await session.refresh(perfil)
    return perfil
