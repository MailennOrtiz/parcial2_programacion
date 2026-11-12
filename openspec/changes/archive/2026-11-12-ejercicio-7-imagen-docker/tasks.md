## 1. Empaquetado

- [x] 1.1 Crear el Dockerfile con dependencias, usuario, Uvicorn y healthcheck.
- [x] 1.2 Excluir archivos locales del contexto y documentar los comandos.

## 2. Verificación

- [x] 2.1 Validar la propuesta OpenSpec y revisar la configuración.
- [x] 2.2 Construir la imagen. El build local generó `libreria:latest` (ID `ee533909fb9c`).
- [x] 2.3 Comprobar el tamaño de la imagen base. Docker informó 74,8 MB en disco, por debajo de 100 MB.
- [x] 2.4 Comprobar arranque, readiness y usuario. Con PostgreSQL 16, Docker informó `running / healthy` y `uid=100(libreria)`.
- [x] 2.5 Comprobar que falla sin configuración (D-05). Uvicorn abortó el arranque con `Falta DATABASE_URL`.
- [x] 2.6 Comprobar el orden del aviso (D-07). El log del contenedor mostró `201 Created` y luego el aviso de la venta 1.
