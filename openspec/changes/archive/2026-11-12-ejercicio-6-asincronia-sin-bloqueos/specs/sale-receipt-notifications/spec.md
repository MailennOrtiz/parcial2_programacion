## Purpose

Simular el aviso del comprobante de cada venta registrada después de responder al cliente, manteniendo la API disponible durante la espera.

## ADDED Requirements

### Requirement: Aviso asincrónico de comprobante

La API SHALL agendar con `BackgroundTasks` un aviso simulado para cada venta registrada exitosamente. La tarea SHALL comenzar después de enviar el cuerpo de la respuesta, esperar con `await asyncio.sleep(0.5)` y registrar un mensaje de nivel INFO que identifique la venta.

#### Scenario: Venta registrada

- **WHEN** se registra correctamente una venta mediante `POST /ventas/`
- **THEN** el cliente recibe HTTP 201 antes de que comience el aviso
- **AND** el aviso queda registrado una vez al finalizar la espera

#### Scenario: Otra petición durante el aviso

- **WHEN** se solicita `GET /health/live` durante la espera del aviso
- **THEN** la API responde HTTP 200 mientras el aviso sigue pendiente

#### Scenario: Venta rechazada

- **WHEN** la API rechaza el alta de una venta
- **THEN** el sistema no agenda el aviso de comprobante
