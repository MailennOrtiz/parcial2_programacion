# Evidencias del parcial

Ver [datos del despliegue](../DEPLOY.md#evidencia-del-vps). D-02 y D-04 se realizaron con EasyPanel.

| Caso | Evidencia |
| --- | --- |
| D-01 | [Tamaños de las imágenes en el VPS](D-01-imagenes-vps.png) |
| D-02 | [Despliegue exitoso](D-02-03-despliegue-exitoso-fecha.png), [arranque de Uvicorn](D-02-04-arranque-uvicorn.png) y [readiness interno](D-02-05-readiness-interno-200.png) |
| D-03 | [Disponibilidad pública](D-03-02-readiness-200.png), [catálogo](D-03-04-catalogo-200.png) y [alta de la venta 2](D-03-05-venta-2-201.png) |
| D-04 | [Venta antes](D-04-01-venta-antes.png), [reemplazo](D-04-02-reemplazo-contenedores.png), [contenedor nuevo healthy](D-04-03-contenedor-nuevo-healthy.png) y [venta después](D-04-04-venta-despues.png) |
| D-05 | [Salida de docker run en el VPS](D-05-docker-run-vps.txt) y [captura del proceso aislado](D-05-D-06-fallo-sin-database-url-y-uid.png) |
| D-06 | [UID 100 del proceso principal](D-05-D-06-fallo-sin-database-url-y-uid.png) |
| D-07 | [201 y aviso de la venta 2](D-07-01-comprobante-venta-2.png) |
| C-07 | [Conteo de SELECT en las pruebas locales con SQLite en memoria](C-07-consultas-sql.txt) |

## Pruebas de conflictos

C-02 ISBN o email repetido 409 con mensaje propio
<img width="1396" height="290" alt="image" src="https://github.com/user-attachments/assets/699168ee-59ca-498e-932c-876987220f89" />
C-03 Segundo perfil para el mismo cliente 409
<img width="1402" height="613" alt="image" src="https://github.com/user-attachments/assets/362ab4dc-f07b-4de3-a8a8-9da0f03a4801" />
