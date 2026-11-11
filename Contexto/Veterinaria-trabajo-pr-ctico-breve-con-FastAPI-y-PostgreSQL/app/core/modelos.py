"""Importa todas las tablas antes de configurar relaciones o crear el esquema."""

from app.modules.duenios.models import Duenio, FichaDuenio
from app.modules.mascotas.models import Mascota
from app.modules.practicas.models import Practica
from app.modules.turnos.models import Turno, TurnoPractica

__all__ = ["Duenio", "FichaDuenio", "Mascota", "Practica", "Turno", "TurnoPractica"]
