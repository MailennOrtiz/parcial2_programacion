"""CORS usa los orígenes del entorno al importar la aplicación."""
import os
import subprocess
import sys
import unittest
from unittest.mock import patch

from app.core.config import obtener_cors_origins


class CorsTest(unittest.TestCase):
    def test_sin_configuracion_no_habilita_origenes(self):
        with patch.dict(os.environ, {}, clear=True), patch("app.core.config.load_dotenv"):
            self.assertEqual(obtener_cors_origins(), [])

    def test_origenes_y_preflight_en_aplicacion_real(self):
        codigo = '''
import asyncio
from httpx import ASGITransport, AsyncClient
from app.main import app

async def comprobar():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://api") as cliente:
        headers = {"Origin": "https://frontend.example.com", "Access-Control-Request-Method": "POST", "Access-Control-Request-Headers": "content-type"}
        respuesta = await cliente.options("/ventas/", headers=headers)
        assert respuesta.status_code == 200
        assert respuesta.headers["access-control-allow-origin"] == "https://frontend.example.com"
        assert "access-control-allow-credentials" not in respuesta.headers
        headers["Origin"] = "https://otro.example.com"
        respuesta = await cliente.options("/ventas/", headers=headers)
        assert respuesta.status_code == 400
        assert "access-control-allow-origin" not in respuesta.headers
        respuesta = await cliente.get("/health/live", headers={"Origin": "http://localhost:5173"})
        assert respuesta.headers["access-control-allow-origin"] == "http://localhost:5173"

asyncio.run(comprobar())
'''
        entorno = os.environ.copy()
        entorno["CORS_ORIGINS"] = " https://frontend.example.com, , http://localhost:5173 "
        resultado = subprocess.run([sys.executable, "-B", "-c", codigo], env=entorno,
                                   capture_output=True, text=True)
        self.assertEqual(resultado.returncode, 0, resultado.stderr)
