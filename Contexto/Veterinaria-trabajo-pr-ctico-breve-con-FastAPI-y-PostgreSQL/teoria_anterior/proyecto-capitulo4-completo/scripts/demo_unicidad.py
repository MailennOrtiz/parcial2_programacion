"""Diapositiva 18: la ventana entre preguntar y escribir. Dispara varias altas SIMULTÁNEAS con el
MISMO nombre y muestra que sólo una entra: el resto recibe 409, sin que el service haya tenido
que "preguntar antes de escribir".

Uso, con el servidor YA corriendo en otra terminal:

    python scripts/demo_unicidad.py

Si ya se corrió una vez, todas reciben 409 (el nombre quedó cargado): python reiniciar.py y otra vez.
"""

import asyncio

import httpx

BASE_URL = "http://127.0.0.1:8000"
NOMBRE_REPETIDO = "Producto disputado"
INTENTOS_SIMULTANEOS = 8


async def un_intento(cliente: httpx.AsyncClient, numero: int) -> tuple[int, int]:
    respuesta = await cliente.post("/productos/", json={"nombre": NOMBRE_REPETIDO, "precio": 999})
    return numero, respuesta.status_code


async def main() -> None:
    print(f"Disparando {INTENTOS_SIMULTANEOS} altas simultáneas, todas con el nombre {NOMBRE_REPETIDO!r}...\n")
    async with httpx.AsyncClient(base_url=BASE_URL, timeout=10) as cliente:
        resultados = await asyncio.gather(
            *(un_intento(cliente, i) for i in range(1, INTENTOS_SIMULTANEOS + 1))
        )

    for numero, codigo in sorted(resultados):
        print(f"  intento {numero}: {codigo}")
    exitosos = [n for n, codigo in resultados if codigo == 201]
    rechazados = [n for n, codigo in resultados if codigo == 409]
    print(f"\nEntraron (201): {len(exitosos)} · rechazados por la base (409): {len(rechazados)}")

    if len(exitosos) == 1 and len(rechazados) == INTENTOS_SIMULTANEOS - 1:
        print("Lo esperado: exactamente UNA entró y la base rechazó las demás, aunque todas "
              "salieron al mismo tiempo.")
    else:
        print("Inesperado: si el nombre ya existía de una corrida anterior, todas reciben 409. "
              "Corré python reiniciar.py y probá otra vez.")


if __name__ == "__main__":
    asyncio.run(main())
