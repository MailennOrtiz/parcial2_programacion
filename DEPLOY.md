# Construcción y ejecución de la imagen

## Construcción

Desde la raíz del repositorio, donde está el Dockerfile:

```bash
docker build --pull -t libreria .
docker images python:3.12-alpine
docker images libreria
```

El límite de 100 MB de la consigna corresponde a la imagen base.

## Ejecución

Preparar un archivo de variables fuera del repositorio, tomando la estructura de
`env.example`. Configurar `DATABASE_URL` con el driver `postgresql+asyncpg` y
los datos de un PostgreSQL accesible desde el contenedor. Configurar
`SQL_ECHO=false`. Reemplazar la ruta y el puerto del ejemplo por los valores
del entorno.

```bash
docker run -d --name libreria \
  -p 8080:8000 \
  --restart unless-stopped \
  --env-file /ruta/privada/libreria.env \
  libreria
```

Si PostgreSQL corre en el host Linux, usar `host.docker.internal` en
`DATABASE_URL` y agregar `--add-host=host.docker.internal:host-gateway`
antes del nombre de la imagen. Si se usa otra dirección, debe ser alcanzable
desde el contenedor.

## Comprobación

```bash
docker ps --filter name=libreria
docker logs libreria
docker exec libreria id
docker exec libreria wget -qO- http://127.0.0.1:8000/health/ready
```

Se espera que el contenedor figure como `healthy`, que el UID sea distinto
de cero y que readiness responda HTTP 200. El arranque crea las tablas en la
base configurada.

Para comprobar el fallo sin configuración, ejecutar
`docker run --rm libreria` y verificar que salga con error por falta de
`DATABASE_URL`. Para D-07, registrar una venta de prueba y revisar que el
mensaje del comprobante aparezca en `docker logs libreria` después del
`201 Created`.

## Resultado local del ejercicio 7

El 12 de noviembre de 2026, el build generó `libreria:latest` (ID
`ee533909fb9c`). Docker informó 74,8 MB en disco para la imagen base.
Con un PostgreSQL 16 de prueba, la API quedó `running / healthy` y
`docker exec … id` informó `uid=100(libreria)`. Sin `DATABASE_URL`,
Uvicorn abortó el arranque. En D-07, los logs del contenedor mostraron
el `201 Created` de la venta 1 antes del aviso simulado del comprobante.

## Evidencia del VPS

Pendiente del ejercicio 8.
