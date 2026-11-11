"""La configuración sale del entorno, no del código.

La dirección de la base se lee de la variable DATABASE_URL, que se define en el archivo `.env`
de la raíz del proyecto (copiar `env.example`). El código sí se sube a un repositorio: se
comparte, se clona y queda en el historial de git aunque después se borre la línea. El `.env`
no se sube nunca (ver `.gitignore`): vive sólo en la máquina de quien lo necesita, y cada
entorno tiene el suyo, con sus propias credenciales.
"""

import os
from pathlib import Path

from dotenv import load_dotenv

load_dotenv(Path(__file__).resolve().parents[2] / ".env")

if "DATABASE_URL" not in os.environ:
    # Mejor una falla clara al arrancar que un error raro diez líneas más adelante.
    raise RuntimeError(
        "Falta la variable DATABASE_URL. Copiá env.example a .env "
        "(en la raíz del proyecto) y completá el valor."
    )

DATABASE_URL: str = os.environ["DATABASE_URL"]

