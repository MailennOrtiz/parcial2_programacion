# Construcción y ejecución de la imagen

## Despliegue rápido en EasyPanel

**Importante para el parcial:** EasyPanel administra los contenedores con su
propio mecanismo. La consigna solicita explícitamente `docker build` y `docker
run` en el VPS, además de evidencia de esos comandos. Confirmar con la cátedra
si acepta EasyPanel como alternativa; de lo contrario usar el procedimiento
manual de abajo para la entrega. No afirmar que EasyPanel equivale a `docker run`.

1. Crear un servicio **App** en el proyecto de EasyPanel. En **Source**, conectar
   el repositorio y la rama que contengan estos cambios, o subir el código.
2. En **Build**, elegir **Dockerfile** con ruta `Dockerfile` y contexto en la
   raíz del proyecto. No seleccionar un builder automático que ignore el archivo.
3. En **Environment**, configurar `DATABASE_URL` y `SQL_ECHO=false`. La URL debe
   usar `postgresql+asyncpg` y los datos de PostgreSQL suministrados. No publicar
   credenciales en Git, logs ni documentación. Si la contraseña tiene caracteres
   especiales, codificarlos para URL.
   Para acceder desde un frontend en otro origen, agregar `CORS_ORIGINS` con sus
   URLs separadas por comas, por ejemplo
   `https://frontend.ejemplo.com,http://localhost:5173`. Sin ruta ni barra final;
   protocolo, dominio y puerto deben coincidir con el frontend. Dejar vacía la
   variable no habilita ningún origen cruzado. Redesplegar después de cambiarla.
4. En **Domains**, configurar el dominio público con destino HTTP al **puerto
   interno 8000**. Habilitar HTTPS según la configuración del panel. No publicar
   el puerto de PostgreSQL.
5. Guardar y pulsar **Deploy**. Revisar los logs de construcción y arranque. La
   aplicación crea las tablas faltantes; si no llega a la base, el arranque falla.
6. Desde la terminal del contenedor de la aplicación ejecutar, solo cuando la
   base del parcial esté vacía y no haya escrituras concurrentes:

   ```bash
   python -m app.datos_iniciales
   ```

   El comando no borra datos y rechaza tablas del dominio con filas existentes.
   Anotar los identificadores de cliente y libros que muestra al terminar: se
   necesitan para probar una venta y pueden no ser 1 y 2.
   Si no hay terminal en la interfaz, acceder por SSH y usar `docker exec` sobre
   el contenedor real de la aplicación, cuyo nombre se identifica con `docker ps`.
7. Desde fuera del VPS comprobar `https://<dominio>/health/ready` y
   `https://<dominio>/libros/`; consultar también `/docs`. Registrar URL, fecha,
   hora, configuración y resultados reales en este documento y en `evidencia/`.
   En `/docs`, usar `POST /ventas/` con los identificadores mostrados por la
   carga, por ejemplo (reemplazar los números por los valores reales):

   ```json
   {"cliente_id": 1, "renglones": [{"libro_id": 1, "cantidad": 2}, {"libro_id": 2, "cantidad": 1}]}
   ```

   Para los precios iniciales y esas cantidades, el total esperado es
   `77000.00`. La venta crea datos reales en la base; no repetirla sin querer.

Dentro de un contenedor, `localhost` apunta a ese contenedor, no al VPS ni a otra
base. Usar la dirección interna que provea el servicio de PostgreSQL o la que
entregue la cátedra; comprobar que sea accesible desde la aplicación. La opción
`--add-host` indicada más abajo corresponde a `docker run` manual y no se debe
suponer que EasyPanel la agrega automáticamente.

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

- **URL pública** [Swagger de la librería](https://app-grupo1-libreria-backend.ldb9fn.easypanel.host/docs).
- **Despliegue exitoso** 12 de noviembre de 2026 a las 20:48:34 (Argentina, UTC−03:00), según el historial de EasyPanel.
- **Servicios** `libreria_backend` en el puerto interno 8000 y PostgreSQL en `libreria_db`. La conexión se configura mediante `DATABASE_URL` en el entorno del servicio.
- **Pruebas públicas** `GET /health/ready` y `GET /libros/` devolvieron 200. `POST /ventas/` devolvió 201 para la venta 2, por 5000.00. El aviso simulado quedó registrado después del 201.
- **Persistencia** EasyPanel reemplazó el contenedor `c814a3e16731` por `059a5713b5db`. El contenedor nuevo quedó `healthy` y `GET /ventas/2` siguió devolviendo 200 con la misma venta.
- **Arranque aislado y usuario** En el VPS, `docker run` sin `DATABASE_URL` terminó con código 3. El proceso principal del backend corrió con UID 100.

Ver el [índice de evidencias](evidencia/README.md).
