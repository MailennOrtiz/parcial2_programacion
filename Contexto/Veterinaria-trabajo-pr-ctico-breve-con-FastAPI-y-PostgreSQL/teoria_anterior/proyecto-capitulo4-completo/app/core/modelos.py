"""Registro de todos los modelos.

Importar este archivo carga todas las tablas en `SQLModel.metadata`. Lo usan `reiniciar.py` (que
crea las tablas con `create_all`) y la aplicación (que necesita todas las clases en memoria para
resolver las relaciones entre módulos, que se nombran con texto).
"""

from app.modules.categorias.models import Categoria  # noqa: F401
from app.modules.ingredientes.models import Ingrediente  # noqa: F401
from app.modules.pedidos.models import DetallePedido, Pedido  # noqa: F401
from app.modules.productos.models import Producto, ProductoIngrediente  # noqa: F401
from app.modules.usuarios.models import Perfil, PerfilSinUnicidad, Usuario  # noqa: F401
