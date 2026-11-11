"""Demostración C-09 contra el servidor real. No lee .env ni modifica la base."""

import argparse
import asyncio
from time import perf_counter

import httpx


async def comprobar(base_url: str, limite_salud: float) -> None:
    async with httpx.AsyncClient(base_url=base_url, timeout=10, trust_env=False) as client:
        # Evita que el tiempo del primer establecimiento de conexión afecte a salud.
        (await client.get("/health/live")).raise_for_status()
        vacunas = ("rabia", "triple", "antirrabica")
        tareas = [asyncio.create_task(client.get(f"/laboratorio/stock/{vacuna}")) for vacuna in vacunas]
        try:
            # Cede el control para que se envíen las tres peticiones antes de salud.
            await asyncio.sleep(0.1)
            inicio = perf_counter()
            salud = await client.get("/health/live")
            duracion = perf_counter() - inicio
            pendientes = sum(not tarea.done() for tarea in tareas)
            print(f"Salud: HTTP {salud.status_code}, {duracion:.3f} s; stock pendientes: {pendientes}/3.")
            salud.raise_for_status()
            if salud.json() != {"estado": "vivo"}:
                raise AssertionError("Respuesta inesperada de /health/live.")
            if duracion >= limite_salud or pendientes != 3:
                raise AssertionError("Salud no respondió a tiempo mientras las tres consultas seguían pendientes.")
            respuestas = await asyncio.gather(*tareas)
            for vacuna, respuesta in zip(vacunas, respuestas):
                respuesta.raise_for_status()
                esperado = {"vacuna": vacuna, "stock": 10 + len(vacuna)}
                if respuesta.json() != esperado:
                    raise AssertionError(f"Stock inesperado para {vacuna}.")
                print(f"Stock {vacuna}: HTTP {respuesta.status_code}, {respuesta.json()['stock']} unidades.")
            print("C-09 aprobado: salud respondió antes de finalizar las tres consultas de stock.")
        finally:
            # No deja peticiones pendientes ni oculta errores de tareas no recogidas.
            await asyncio.gather(*tareas, return_exceptions=True)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--base-url", default="http://localhost:8000")
    parser.add_argument("--limite-salud", type=float, default=0.5, help="Límite en segundos (por defecto: 0.5).")
    args = parser.parse_args()
    if args.limite_salud <= 0:
        parser.error("--limite-salud debe ser mayor que cero.")
    try:
        asyncio.run(comprobar(args.base_url, args.limite_salud))
    except (httpx.HTTPError, AssertionError) as error:
        print(f"C-09 falló: {error}")
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
