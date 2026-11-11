from sqlmodel import SQLModel

from app.modules.pedidos.schemas import PedidoRead


# ─── Usuario ─────────────────────────────────────────────────────────────────
class UsuarioCreate(SQLModel):
    # Sin id: lo asigna la base (el próximo después de los datos iniciales es el 9).
    nombre: str


class UsuarioRead(SQLModel):
    """Exactamente las columnas de la tabla. No hay `pedidos` (diapositiva 4)."""

    id: int
    nombre: str


# ─── Perfil (uno a uno) ──────────────────────────────────────────────────────
class PerfilCreate(SQLModel):
    apodo: str


class PerfilRead(SQLModel):
    id: int
    usuario_id: int
    apodo: str


# ═══════════════════════════════════════════════════════════════════════════
# PARTE 2 · CÓMO SE LEEN
# ═══════════════════════════════════════════════════════════════════════════


# ─── diapositiva 11: las dos puntas del hilo ────────────────────────
class UsuarioConPrimerPedidoCreate(SQLModel):
    """Alta de un usuario junto con su primer pedido, en una sola petición.

    Sin ids: el del usuario y el del pedido los asigna la base al guardar.
    """

    nombre: str


class AntesDeGuardar(SQLModel):
    """Cómo estaba el pedido en memoria ANTES de mandar nada a la base."""

    pedido_usuario_es_el_usuario: bool
    pedido_usuario_id: int | None


class UsuarioConPrimerPedidoRead(SQLModel):
    antes_de_guardar: AntesDeGuardar
    usuario: UsuarioRead
    pedido: PedidoRead


# ─── diapositiva 12: qué hay en memoria ─────────────────────────────
class QueHayEnMemoria(SQLModel):
    consultas_emitidas: int
    usuario: UsuarioRead
    atributos_cargados: list[str]
    atributos_sin_cargar: list[str]


# ─── diapositiva 14: el usuario con sus pedidos, precargados ────────
class UsuarioConPedidos(SQLModel):
    id: int
    nombre: str
    pedidos: list[PedidoRead]


class UsuarioConPedidosYConsultas(SQLModel):
    consultas_emitidas: int
    usuario: UsuarioConPedidos
