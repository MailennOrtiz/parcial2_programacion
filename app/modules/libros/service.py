# L�gica del m�dulo libros (se implementa en ejercicios posteriores).
"""Operaciones de libros con relaciones precargadas."""
from fastapi import HTTPException
from sqlalchemy.orm import joinedload, selectinload, raiseload
from sqlmodel import select
from app.core import crud
from app.modules.libros.models import Libro, LibroAutor
from app.modules.libros.schemas import LibroRead, LibroResumenRead, AutoriaRead

def opciones(detalle=False):
    cargas = [joinedload(Libro.editorial), joinedload(Libro.genero), raiseload("*")]
    if detalle:
        cargas.append(selectinload(Libro.autorias).joinedload(LibroAutor.autor))
    return cargas

def lectura(libro):
    return LibroRead(id=libro.id, isbn=libro.isbn, titulo=libro.titulo,
        precio=libro.precio, stock=libro.stock, editorial=libro.editorial,
        genero=libro.genero, autores=[AutoriaRead.model_validate(a) for a in
            sorted(libro.autorias, key=lambda a: (a.orden, a.autor_id))])

def lectura_resumen(libro):
    return LibroResumenRead(id=libro.id, isbn=libro.isbn, titulo=libro.titulo,
        precio=libro.precio, stock=libro.stock, editorial=libro.editorial,
        genero=libro.genero)

async def obtener(session, identificador):
    consulta = (select(Libro).where(Libro.id == identificador)
        .options(*opciones(True)).execution_options(populate_existing=True))
    libro = (await session.exec(consulta)).first()
    if libro is None:
        raise HTTPException(status_code=404, detail="Libro no encontrado.")
    return libro

async def crear(session, datos):
    libro = Libro(**datos.model_dump(exclude={"autores"}),
        autorias=[LibroAutor(**autor.model_dump()) for autor in datos.autores])
    await crud.guardar(session, libro)
    return lectura(await obtener(session, libro.id))

async def actualizar(session, identificador, datos):
    libro = await obtener(session, identificador)
    libro.sqlmodel_update(datos.model_dump(exclude_unset=True))
    await crud.guardar(session, libro)
    return lectura(await obtener(session, identificador))

async def listar(session, limit, offset, titulo=None, genero_id=None, editorial_id=None):
    consulta = select(Libro).options(*opciones())
    if titulo is not None:
        # autoescape trata %, _ y la sintaxis SQL como texto literal del usuario.
        consulta = consulta.where(Libro.titulo.icontains(titulo, autoescape=True))
    if genero_id is not None:
        consulta = consulta.where(Libro.genero_id == genero_id)
    if editorial_id is not None:
        consulta = consulta.where(Libro.editorial_id == editorial_id)
    libros = (await session.exec(consulta.order_by(Libro.id).limit(limit).offset(offset))).all()
    return [lectura_resumen(l) for l in libros]
