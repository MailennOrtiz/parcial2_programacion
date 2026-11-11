# L�gica del m�dulo ventas (se implementa en ejercicios posteriores).
"""Ventas con precios históricos y lecturas precargadas."""
from datetime import datetime, timezone
from decimal import Decimal
from fastapi import HTTPException
from sqlalchemy.orm import joinedload, selectinload, raiseload
from sqlmodel import select
from app.core import crud
from app.modules.libros.models import Libro
from app.modules.ventas.models import Venta, RenglonVenta
from app.modules.ventas.schemas import VentaRead, RenglonRead

def opciones():
    return [joinedload(Venta.cliente),
        selectinload(Venta.renglones).joinedload(RenglonVenta.libro), raiseload("*")]

def lectura(venta):
    return VentaRead(id=venta.id, fecha=venta.fecha, total=venta.total, cliente=venta.cliente,
        renglones=[RenglonRead(libro_id=r.libro_id, titulo=r.libro.titulo,
            cantidad=r.cantidad, precio_unitario=r.precio_unitario,
            subtotal=r.precio_unitario * r.cantidad)
            for r in sorted(venta.renglones, key=lambda r: r.id)])

async def obtener(session, identificador):
    consulta = (select(Venta).where(Venta.id == identificador).options(*opciones())
        .execution_options(populate_existing=True))
    venta = (await session.exec(consulta)).first()
    if venta is None:
        raise HTTPException(status_code=404, detail="Venta no encontrada.")
    return lectura(venta)

async def listar(session, limit, offset, cliente_id=None):
    consulta = select(Venta).options(*opciones())
    if cliente_id is not None:
        consulta = consulta.where(Venta.cliente_id == cliente_id)
    ventas = (await session.exec(consulta.order_by(Venta.id).limit(limit).offset(offset))).all()
    return [lectura(v) for v in ventas]

async def crear(session, datos):
    ids = [r.libro_id for r in datos.renglones]
    precios = dict((await session.exec(select(Libro.id, Libro.precio).where(Libro.id.in_(ids)))).all())
    if len(precios) != len(ids):
        raise HTTPException(status_code=409, detail="Uno o más libros no existen.")
    renglones = [RenglonVenta(libro_id=r.libro_id, cantidad=r.cantidad,
        precio_unitario=precios[r.libro_id]) for r in datos.renglones]
    total = sum((r.precio_unitario * r.cantidad for r in renglones), Decimal("0.00"))
    venta = Venta(cliente_id=datos.cliente_id, fecha=datetime.now(timezone.utc),
        total=total, renglones=renglones)
    await crud.guardar(session, venta)
    return await obtener(session, venta.id)
