# Evidencias pendientes del parcial

Esta carpeta es una guía: **no contiene resultados de un despliegue real**.
Guardar aquí salidas reales, sin contraseñas, variables de entorno ni datos
sensibles. Anotar fecha, URL pública y contexto de cada comprobación en `DEPLOY.md`.

- **C-07:** consultas SQL de los detalles de libro y venta, comparando uno y varios
  autores o renglones con `SQL_ECHO=true` en un entorno de prueba; volver a
  `SQL_ECHO=false` en el VPS.
- **D-01:** `docker images` con la imagen base y la del proyecto.
- **D-02:** construcción, ejecución, estado `healthy` y logs de arranque.
- **D-03:** desde afuera, `/health/ready`, `/libros/` y alta real de una venta.
- **D-04:** recreación del contenedor y comprobación de persistencia, únicamente
  cuando corresponda y con autorización para operar sobre el VPS.
- **D-05:** ejecución sin `DATABASE_URL`, que debe terminar con error.
- **D-06:** `docker exec ... id`, usuario diferente de root.
- **D-07:** log real del aviso de la venta después del `201 Created`.

La consigna pide explícitamente `docker run`. Si se usa EasyPanel, consultar con
la cátedra cómo documentar la equivalencia antes de asumir que cumple D-02/D-04.
