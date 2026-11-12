## Why

El ejercicio 6 del parcial exige que el alta de una venta envíe la respuesta antes de ejecutar el aviso simulado del comprobante.

## What Changes

- Agendar el aviso de cada venta exitosa con `BackgroundTasks`.
- Simular la espera de medio segundo con `asyncio.sleep` y registrar el ID de la venta en el log.
- Verificar el orden de la respuesta y la atención de otras peticiones durante la espera.

## Capabilities

### New Capabilities

- `sale-receipt-notifications`: aviso simulado del comprobante en segundo plano.

### Modified Capabilities

Ninguna.

## Impact

Afecta al alta de ventas y a las pruebas HTTP. Conserva el contrato de `POST /ventas/`.
