from sqlmodel import SQLModel


# ─── Pedido ──────────────────────────────────────────────────────────────────
# Al crear un pedido viajan DOS relaciones, y no viajan igual:
#   - asociación (Usuario — Pedido): viaja `usuario_id`, el id de un usuario
#     que YA existe. El usuario no se crea ni se modifica: se lo nombra.
#   - composición (Pedido ◆ DetallePedido): viajan los DATOS de cada línea,
#     en `detalles`. La línea no existe antes que el pedido: nace con él, así
#     que no hay ningún id de línea que mandar.
class DetalleEnPedidoCreate(SQLModel):
    """Una línea que viaja ADENTRO del pedido (composición).

    No trae `id` (lo pone la base) ni `pedido_id` (el pedido se crea en la
    misma petición: todavía no tiene número). Trae los datos de la línea.
    `producto_id` sí es un id: el producto ya existe y la línea sólo lo nombra.
    """

    producto_id: int
    cantidad: int


class PedidoCreate(SQLModel):
    # Sin id: el número del pedido lo asigna la base (el próximo después de
    # los datos iniciales es el 104).
    usuario_id: int  # asociación: el id de un usuario que ya existe
    # composición: los datos de las líneas. Si no se mandan, el pedido nace sin líneas.
    detalles: list[DetalleEnPedidoCreate] = []


class PedidoRead(SQLModel):
    """La fila tal cual está guardada: `usuario_id` es un número y nada más."""

    id: int
    usuario_id: int


class PedidoConUsuario(SQLModel):
    """Resultado del JOIN: con el número se llegó al dueño."""

    id: int
    usuario_id: int
    usuario: str


# ─── Líneas del pedido ───────────────────────────────────────────────────────
class DetalleCreate(SQLModel):
    producto_id: int
    cantidad: int


class DetalleRead(SQLModel):
    id: int
    pedido_id: int
    producto_id: int
    producto: str
    cantidad: int


# ═══════════════════════════════════════════════════════════════════════════
# PARTE 2 · CÓMO SE LEEN
# ═══════════════════════════════════════════════════════════════════════════
# Estos esquemas tienen campos ANIDADOS (`usuario`, `detalles`). Para
# armarlos, FastAPI lee esos atributos del objeto Pedido: si la relación no
# estaba precargada, ese acceso sería justamente la carga perezosa prohibida.
# Por eso sólo se usan en los endpoints que precargan (diapositiva 14).


class LineaDelPedido(SQLModel):
    id: int
    producto_id: int
    cantidad: int


class UsuarioDelPedido(SQLModel):
    id: int
    nombre: str


class PedidoConLineas(SQLModel):
    """Un pedido con sus líneas adentro (diapositivas 13 y 14)."""

    id: int
    usuario_id: int
    detalles: list[LineaDelPedido]


class PedidosConLineasYConsultas(SQLModel):
    """El listado más cuántas consultas hicieron falta para armarlo."""

    consultas_emitidas: int
    pedidos: list[PedidoConLineas]


class PedidoCompleto(SQLModel):
    """El pedido con su usuario y sus líneas: `obtener_con_detalles` (diap. 14)."""

    id: int
    usuario: UsuarioDelPedido
    detalles: list[LineaDelPedido]


class PedidoCompletoYConsultas(SQLModel):
    consultas_emitidas: int
    pedido: PedidoCompleto


class FilaDelJoin(SQLModel):
    """Una fila tal como la devuelve el JOIN (diapositiva 14).

    Los datos del pedido (`pedido_id`, `usuario_id`) se repiten en cada línea.
    Un pedido sin líneas aparece igual, con los campos de la línea vacíos.
    """

    pedido_id: int
    usuario_id: int
    linea_id: int | None
    producto_id: int | None
    cantidad: int | None


class FilasDelJoinYConsultas(SQLModel):
    consultas_emitidas: int
    filas: list[FilaDelJoin]


# ═══════════════════════════════════════════════════════════════════════════
# LA VUELTA DE POST /pedidos/ · COMPOSICIÓN Y ASOCIACIÓN
# ═══════════════════════════════════════════════════════════════════════════
class PedidoConDetallesRead(SQLModel):
    """Lo que devuelve el alta de un pedido: lo que quedó guardado, armado.

    `usuario_id` es lo que se guardó (la clave foránea de la asociación) y
    `usuario` viene armado para leerlo. `detalles` son las líneas de la
    composición, con el id que les puso la base al guardarlas.
    """

    id: int
    usuario_id: int
    usuario: UsuarioDelPedido
    detalles: list[LineaDelPedido]
