# Evidencia C-09 — Laboratorio sin bloquear salud

Comprobación realizada el 4 de noviembre de 2026 contra el servidor Uvicorn
en ejecución en `127.0.0.1:8000`, con un solo worker.

## Comando

```powershell
.\.venv\Scripts\python.exe test/c09_concurrencia.py --base-url http://127.0.0.1:8000
```

## Salida real

```text
Salud: HTTP 200, 0.005 s; stock pendientes: 3/3.
Stock rabia: HTTP 200, 15 unidades.
Stock triple: HTTP 200, 16 unidades.
Stock antirrabica: HTTP 200, 21 unidades.
C-09 aprobado: salud respondió antes de finalizar las tres consultas de stock.
```

El proceso terminó con código 0. Se hicieron peticiones HTTP reales, no se usó
el transporte ASGI de las pruebas unitarias. No hubo acceso a la base de datos.

## Conclusión

La salud respondió en 0,005 segundos cuando las tres consultas de stock todavía
estaban pendientes. Las tres terminaron con HTTP 200 y el stock esperado. La espera
sincrónica del laboratorio no impidió atender la petición de salud.
