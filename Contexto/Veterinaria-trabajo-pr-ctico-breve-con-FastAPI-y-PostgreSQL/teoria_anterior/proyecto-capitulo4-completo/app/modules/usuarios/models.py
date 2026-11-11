"""Usuario y sus perfiles.

Parte 1 (cómo se guardan):
  Diapositiva 4 — uno a muchos: qué NO tiene la tabla del lado "uno".
  Diapositiva 5 — uno a uno: clave foránea MÁS restricción de unicidad.

Parte 2 (cómo se leen):
  Diapositiva 11 — `Usuario.pedidos`, la otra punta de `Pedido.usuario`.
  Diapositiva 12 — `usuario.pedidos` parece una lista, pero es una consulta.

Regla para leer todos los `models.py` de este proyecto: los `Field(...)` son
lo que se GUARDA (columnas, claves foráneas, restricciones: Parte 1). Los
`Relationship(...)` son cómo se NAVEGA desde Python (Parte 2): no agregan
ninguna columna a la base.
"""

from typing import TYPE_CHECKING, Optional

from sqlmodel import Field, Relationship, SQLModel

if TYPE_CHECKING:
    # Sólo para las anotaciones: evita el import circular en tiempo de ejecución
    # (pedidos/models.py también menciona a Usuario).
    from app.modules.pedidos.models import Pedido


class Usuario(SQLModel, table=True):
    """El lado "uno". Mirá lo que NO tiene: ninguna columna de pedidos.

    En el diagrama de clases el usuario "tiene" una lista de pedidos. En la
    tabla no hay dónde ponerla: una columna guarda un valor, no una lista.
    La ficha de Marta no lleva los vales colgados (diapositiva 4).
    """

    id: int | None = Field(default=None, primary_key=True)
    nombre: str

    # ── diapositivas 11 y 12 ─────────────────────────────────────────
    # La otra punta de `Pedido.usuario`. Sigue sin haber una columna de
    # pedidos en la tabla: `usuario.pedidos` es una CONSULTA que el ORM sabe
    # armar (SELECT ... FROM pedido WHERE usuario_id = ...), no una lista
    # guardada en la fila. La ficha dice «ver depósito» (diapositiva 12).
    # Declararla no la ejecuta: en este proyecto, tocarla sin precargarla
    # explota (diapositiva 15).
    pedidos: list["Pedido"] = Relationship(back_populates="usuario")

    # ── Uno a uno, navegado (diap. 5, diap. 11) ──────────
    # `usuario.perfil` es UN perfil o ninguno, no una lista: uselist=False.
    # Esa promesa la puede hacer el ORM porque la base la garantiza con
    # `unique=True` en `Perfil.usuario_id`.
    # passive_deletes=True: qué pasa con el perfil al borrar el usuario lo
    # decide la base, no el ORM (hoy, sin ON DELETE, la base lo impide).
    perfil: Optional["Perfil"] = Relationship(
        back_populates="usuario",
        passive_deletes=True,
        sa_relationship_kwargs={"uselist": False},
    )

    # El contraejemplo, navegado con honestidad: como la tabla NO tiene
    # unicidad, un usuario puede tener dos (diapositiva 5). Declararlo con
    # uselist=False sería mentir: el ORM esperaría uno y la base admite varios.
    # Por eso es una lista: sin la restricción, es un uno a muchos.
    perfiles_sin_unicidad: list["PerfilSinUnicidad"] = Relationship(
        back_populates="usuario", passive_deletes=True
    )


class Perfil(SQLModel, table=True):
    """Uno a uno bien hecho: "un socio, un carnet" (diapositiva 5).

    La única diferencia con un uno a muchos es `unique=True`. Con eso la base
    rechaza un segundo perfil para el mismo usuario.

    (Usuario–Perfil es un ejemplo de esta presentación: el capítulo enuncia
    la regla pero no da un caso concreto.)
    """

    id: int | None = Field(default=None, primary_key=True)
    usuario_id: int = Field(foreign_key="usuario.id", unique=True)
    apodo: str

    # La otra punta de `Usuario.perfil`.
    usuario: Usuario = Relationship(back_populates="perfil")


class PerfilSinUnicidad(SQLModel, table=True):
    """CONTRAEJEMPLO deliberado: lo mismo que `Perfil`, sin `unique=True`.

    Existe sólo para mostrar qué pasa cuando falta la restricción: la base
    acepta dos perfiles del mismo usuario. Es un uno a muchos que tenía un
    solo elemento por casualidad (diapositiva 5).
    """

    __tablename__ = "perfil_sin_unicidad"

    id: int | None = Field(default=None, primary_key=True)
    usuario_id: int = Field(foreign_key="usuario.id")  # <- falta unique=True
    apodo: str

    # La otra punta de `Usuario.perfiles_sin_unicidad`.
    usuario: Usuario = Relationship(back_populates="perfiles_sin_unicidad")
