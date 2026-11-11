"""Importa todas las tablas antes de configurar relaciones o crear el esquema."""

from app.modules.editoriales.models import Editorial
from app.modules.generos.models import Genero
from app.modules.autores.models import Autor
from app.modules.libros.models import Libro, LibroAutor
from app.modules.clientes.models import Cliente, PerfilCliente
from app.modules.ventas.models import Venta, RenglonVenta

__all__ = [
    "Editorial",
    "Genero",
    "Autor",
    "Libro",
    "LibroAutor",
    "Cliente",
    "PerfilCliente",
    "Venta",
    "RenglonVenta",
]