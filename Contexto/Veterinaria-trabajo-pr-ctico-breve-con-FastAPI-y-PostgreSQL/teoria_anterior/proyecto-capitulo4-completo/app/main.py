"""Capítulo 4 completo: el proyecto que acompaña a Capitulo-4-Completo.pptx.

Junta los dos proyectos del capítulo en un solo esquema:
  - Partes 1 y 2 (diapositivas 2 a 15): cómo se guardan y cómo se leen las relaciones.
  - Parte 3 (diapositivas 16 a 19): CHECK y unicidad en la base. La 19 (migraciones) es
    conceptual: este proyecto no usa Alembic.

Antes de levantarlo: `python reiniciar.py`, que crea las tablas y carga los datos de las
diapositivas. Ver README.md.
"""

from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

import app.core.modelos  # noqa: F401  (registra todas las tablas y sus relaciones)
from app.core.database import crear_fabrica_de_sesiones, crear_motor
from app.modules.categorias.router import router as categorias_router
from app.modules.health.router import router as health_router
from app.modules.ingredientes.router import router as ingredientes_router
from app.modules.pedidos.router import router as pedidos_router
from app.modules.productos.router import router as productos_router
from app.modules.usuarios.router import router as usuarios_router

# carpeta static/ vive adentro de app/
DIR_ESTATICOS = Path(__file__).resolve().parent / "static"


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lo de antes del yield corre UNA vez al arrancar; lo de después, UNA vez al apagar.

    El motor se crea acá: ni por petición (sería abrir un pool nuevo cada vez) ni al importar el
    archivo, que ocurre antes de que haya un bucle de eventos (EA-08, Capítulo 1, sección 1.9).

    Las tablas no se crean acá: las crea `python reiniciar.py`, que además vuelve a cargar los
    datos de las diapositivas.
    """
    app.state.motor = crear_motor()
    app.state.fabrica_de_sesiones = crear_fabrica_de_sesiones(app.state.motor)
    yield
    # Al apagar: las conexiones del pool vuelven al servidor, ordenadamente.
    await app.state.motor.dispose()


app = FastAPI(
    title="Capítulo 4 completo — persistencia: SQLModel, PostgreSQL y el modelo de datos",
    version="1.0.0",
    description=(
        "El proyecto que acompaña a la presentación del capítulo 4, diapositiva por diapositiva.\n\n"
        "**Parte 1 · cómo se guardan las relaciones** (diapositivas 3 a 8): clave foránea, uno a "
        "muchos, uno a uno, muchos a muchos con dato propio, agregación y composición, qué pasa al "
        "borrar y el índice de la clave foránea.\n\n"
        "**Parte 2 · cómo se leen** (diapositivas 10 a 15): `Relationship()` con `back_populates`, "
        "declarar no es cargar, el N+1, `selectinload`, la excepción `MissingGreenlet` y "
        "`joinedload`. Esas respuestas traen `consultas_emitidas`.\n\n"
        "**Parte 3 · el esquema en la práctica** (diapositivas 17 y 18): CHECK y unicidad en la "
        "base.\n\n"
        "Páginas para probarlo en vivo: [la página de inicio](/)."
    ),
    lifespan=lifespan,
)

app.include_router(health_router)
app.include_router(usuarios_router)
app.include_router(pedidos_router)
app.include_router(categorias_router)
app.include_router(productos_router)
app.include_router(ingredientes_router)

app.mount("/static", StaticFiles(directory=DIR_ESTATICOS), name="static")


@app.get("/", include_in_schema=False)
async def raiz():
    """La página de inicio, con las dos páginas de demostración. No es un endpoint de la API:
    por eso no aparece en /docs."""
    return FileResponse(DIR_ESTATICOS / "index.html")
