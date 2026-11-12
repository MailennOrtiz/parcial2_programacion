## Context

Las rutas ya son asincrónicas y usan sesiones asincrónicas. El servicio de ventas devuelve el contrato de lectura después de guardar la venta.

## Goals / Non-Goals

**Goals:** enviar el 201 antes del aviso y mantener disponible el servidor durante la espera.

**Non-Goals:** enviar correos reales o agregar infraestructura de colas.

## Decisions

- Agendar el aviso en el router después de que el servicio devuelve la venta guardada. Pasar solo el ID, para evitar que la tarea dependa de la sesión de la petición.
- Usar un logger bajo `uvicorn.error` para que el evento de nivel INFO sea visible con la configuración habitual de Uvicorn.
- Probar el orden observando los mensajes ASGI y comprobar la concurrencia con una espera controlada. Verificar por separado el retardo de medio segundo.

## Risks / Trade-offs

La simulación se ejecuta en el proceso de la API y termina si ese proceso se interrumpe.
