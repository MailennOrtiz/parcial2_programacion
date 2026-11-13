# L�gica del m�dulo autores (se implementa en ejercicios posteriores).
"""Operaciones de autores."""
from sqlalchemy.orm import joinedload, raiseload
from sqlmodel import select
from app.core import crud
from app.modules.autores.models import Autor
from app.modules.libros.models import Libro, LibroAutor
from app.modules.libros.schemas import LibroResumenRead, LibroDeAutorRead

async def crear(session, datos):
    objeto = Autor.model_validate(datos)
    await crud.guardar(session, objeto)
    return objeto

async def obtener(session, identificador):
    return await crud.obtener(session, Autor, identificador)

async def listar(session, limit, offset):
    return await crud.listar(session, Autor, limit, offset)

async def actualizar(session, identificador, datos):
    return await crud.actualizar(session, Autor, identificador, datos)

async def libros(session, identificador, limit, offset):
    await obtener(session, identificador)
    consulta = (select(LibroAutor).where(LibroAutor.autor_id == identificador)
        .options(joinedload(LibroAutor.libro).joinedload(Libro.editorial),
                 joinedload(LibroAutor.libro).joinedload(Libro.genero), raiseload("*"))
        .order_by(LibroAutor.orden, LibroAutor.libro_id).limit(limit).offset(offset))
    autorias = (await session.exec(consulta)).all()
    return [LibroDeAutorRead(
        libro=LibroResumenRead(id=a.libro.id, isbn=a.libro.isbn, titulo=a.libro.titulo,
            precio=a.libro.precio, stock=a.libro.stock, editorial=a.libro.editorial,
            genero=a.libro.genero),
        rol=a.rol, orden=a.orden) for a in autorias]
