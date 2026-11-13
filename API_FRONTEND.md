# Guía de integración del frontend

Esta guía describe los endpoints implementados actualmente. La documentación
interactiva generada por la aplicación, con los esquemas completos y posibilidad
de probar las rutas, está en `BASE_URL/docs`; el contrato OpenAPI está en
`BASE_URL/openapi.json` y también hay documentación en `BASE_URL/redoc`.

En local, `BASE_URL` suele ser `http://127.0.0.1:8000`. En el servidor,
reemplazarlo por la URL pública real, por ejemplo `https://api.ejemplo.com`.
No incluir contraseñas ni `DATABASE_URL` en el frontend.

## Consideraciones para integrar

- Las rutas no tienen prefijo `/api`. Las colecciones usan barra final, por
  ejemplo `/libros/`; las rutas con ID y subrutas se escriben como en la tabla.
- Enviar JSON con `Content-Type: application/json` en POST y PATCH.
- No hay autenticación ni autorización implementadas.
- **CORS:** configurar en el backend `CORS_ORIGINS` con los orígenes del
  frontend separados por comas, por ejemplo
  `https://frontend.ejemplo.com,http://localhost:5173`. Cada origen incluye
  protocolo, dominio y puerto si corresponde, sin ruta ni barra final. Si la
  variable está vacía, no se autoriza ningún origen cruzado. Redesplegar al
  cambiarla. Que funcione en Postman o Swagger no garantiza que el navegador
  permita peticiones desde otro origen. CORS no sustituye autenticación.
- Los IDs de ejemplo no están garantizados. Usar los devueltos por la API o por
  el comando de carga inicial; en particular, no hay listado de clientes ni de
  autores en la versión actual.
- Los importes se representan como `Decimal` y se envían en las respuestas como
  cadenas, por ejemplo `"25000.00"`. Para importes evitar cálculos con `float`
  sin una estrategia de precisión decimal; los totales de venta los calcula el
  servidor.
- Los contratos de entrada rechazan campos extra, incluido `id` en las altas.

## Rutas disponibles

En los listados `limit` va de 1 a 100 y vale 20 por defecto; `offset` empieza
en 0 y vale 0 por defecto. Las respuestas son **arrays JSON**, no un objeto
envoltorio con `items` o `total`.

| Método | Ruta | Uso |
|---|---|---|
| GET | `/health/live` | Estado del proceso, sin consultar la base. |
| GET | `/health/ready` | Disponibilidad de la base. |
| POST | `/editoriales/` | Crear editorial. |
| GET | `/editoriales/?limit=20&offset=0` | Listar editoriales. |
| GET | `/editoriales/{id}` | Ver editorial. |
| PATCH | `/editoriales/{id}` | Modificar campos enviados. |
| GET | `/editoriales/{id}/libros?limit=20&offset=0` | Libros de una editorial. |
| POST | `/generos/` | Crear género. |
| GET | `/generos/?limit=20&offset=0` | Listar géneros. |
| GET | `/generos/{id}/libros?limit=20&offset=0` | Libros de un género. |
| POST | `/autores/` | Crear autor. |
| GET | `/autores/{id}` | Ver autor. |
| PATCH | `/autores/{id}` | Modificar campos enviados. |
| GET | `/autores/{id}/libros?limit=20&offset=0` | Libros de un autor, con rol y orden. |
| POST | `/libros/` | Crear libro con autorías. |
| GET | `/libros/?limit=20&offset=0&titulo=ray&genero_id=1` | Listar y filtrar libros. |
| GET | `/libros/{id}` | Ver libro con editorial, género y autores. |
| PATCH | `/libros/{id}` | Modificar los campos escalares del libro. |
| POST | `/clientes/` | Crear cliente. |
| GET | `/clientes/{id}` | Ver cliente y perfil opcional. |
| PATCH | `/clientes/{id}` | Modificar nombre o email. |
| POST | `/clientes/{id}/perfil` | Crear perfil del cliente. |
| GET | `/clientes/{id}/ventas?limit=20&offset=0` | Ventas del cliente. |
| POST | `/ventas/` | Registrar venta con sus renglones. |
| GET | `/ventas/?limit=20&offset=0` | Listar ventas. |
| GET | `/ventas/{id}` | Ver venta con cliente y renglones. |

No están implementadas operaciones DELETE, modificación de ventas, ni edición
de las autorías desde `PATCH /libros/{id}`. El filtro de título es parcial y no
distingue mayúsculas.

## Cuerpos de creación y actualización

Los siguientes son ejemplos; los IDs deben existir realmente.

**Editorial** — `POST /editoriales/`:

```json
{"nombre": "Editorial Sur", "pais": "Argentina"}
```

`pais` es opcional y puede ser `null`. En `PATCH /editoriales/{id}` se envían
solo los campos a cambiar; `nombre` no acepta `null`.

**Género** — `POST /generos/`:

```json
{"nombre": "Novela"}
```

**Autor** — `POST /autores/`:

```json
{"nombre": "Julio Cortázar", "nacionalidad": "Argentina"}
```

`nacionalidad` es opcional y puede ser `null`. En `PATCH /autores/{id}` se
pueden enviar `nombre` y/o `nacionalidad`; `nombre` no acepta `null`.

**Libro** — `POST /libros/`:

```json
{
  "isbn": "978-950-00-0001-1",
  "titulo": "Rayuela",
  "precio": "25000.00",
  "stock": 10,
  "editorial_id": 1,
  "genero_id": 1,
  "autores": [{"autor_id": 1, "rol": "autor", "orden": 1}]
}
```

`precio` debe ser mayor a cero, con hasta 10 dígitos y 2 decimales; `stock`
debe ser un entero no negativo. `genero_id` puede omitirse o ser `null`.
`autores` puede omitirse y por defecto es una lista vacía. Los roles permitidos
son `autor`, `coautor`, `traductor` e `ilustrador`; `orden` es un entero desde 1.

`PATCH /libros/{id}` acepta `isbn`, `titulo`, `precio`, `stock`, `editorial_id`
y `genero_id`; solo `genero_id` admite `null`. No acepta `autores`.

**Cliente** — `POST /clientes/`:

```json
{"nombre": "Tomás Ríos", "email": "tomas@example.com"}
```

El email debe tener formato válido. `PATCH /clientes/{id}` acepta `nombre` y/o
`email` sin `null`.

**Perfil** — `POST /clientes/{id}/perfil`:

```json
{"telefono": "12345678", "direccion": "Calle 123"}
```

Un cliente puede tener como máximo un perfil.

**Venta** — `POST /ventas/`:

```json
{
  "cliente_id": 1,
  "renglones": [
    {"libro_id": 1, "cantidad": 2},
    {"libro_id": 2, "cantidad": 1}
  ]
}
```

Debe haber al menos un renglón; no se puede repetir un libro y cada cantidad
debe ser un entero positivo. No enviar fecha, precios ni total: el servidor los
genera. Los precios quedan guardados en la venta aunque cambie el catálogo.

## Formato de respuestas

Un libro en `GET /libros/` incluye editorial y género, pero no la lista de
autores. El detalle o alta agrega `autores`:

```json
{
  "id": 1,
  "isbn": "978-950-00-0001-1",
  "titulo": "Rayuela",
  "precio": "25000.00",
  "stock": 10,
  "editorial": {"id": 1, "nombre": "Editorial Sur", "pais": "Argentina"},
  "genero": {"id": 1, "nombre": "Novela"},
  "autores": [
    {"autor": {"id": 1, "nombre": "Julio Cortázar", "nacionalidad": "Argentina"}, "rol": "autor", "orden": 1}
  ]
}
```

`genero` puede ser `null`. En `GET /autores/{id}/libros` cada elemento tiene
forma `{"libro": {...}, "rol": "autor", "orden": 1}`; el libro es el resumen
con editorial y género. Un cliente se devuelve como
`{"id": 1, "nombre": "...", "email": "...", "perfil": null}`; si existe,
`perfil` contiene `id`, `cliente_id`, `telefono` y `direccion`.

Ejemplo de venta:

```json
{
  "id": 1,
  "fecha": "2026-11-12T15:00:00Z",
  "total": "77000.00",
  "cliente": {"id": 1, "nombre": "Tomás Ríos", "email": "tomas@example.com"},
  "renglones": [
    {"libro_id": 1, "titulo": "Rayuela", "cantidad": 2, "precio_unitario": "25000.00", "subtotal": "50000.00"},
    {"libro_id": 2, "titulo": "Otro libro", "cantidad": 1, "precio_unitario": "27000.00", "subtotal": "27000.00"}
  ]
}
```

El formato exacto de la zona horaria de `fecha` puede variar; interpretarla
como fecha ISO 8601, no como texto con un único formato fijo.

## Estados y errores

| Estado | Significado |
|---|---|
| 200 | Consulta o actualización exitosa. |
| 201 | Recurso creado. |
| 404 | Recurso no encontrado. |
| 409 | Conflicto de integridad, por ejemplo ISBN duplicado o referencia inexistente. |
| 422 | Cuerpo, identificador o parámetros inválidos. |
| 503 | La base no responde en `/health/ready`. |

Los errores de aplicación suelen tener forma `{"detail": "mensaje"}`. Los
errores de validación 422 de FastAPI usan `detail` como lista de objetos, no
como cadena; el frontend debe contemplar ambas formas.

## Ejemplo con `fetch`

```js
const BASE_URL = "https://api.ejemplo.com"; // reemplazar por la URL real

async function api(ruta, opciones = {}) {
  const respuesta = await fetch(`${BASE_URL}${ruta}`, {
    ...opciones,
    headers: { "Content-Type": "application/json", ...opciones.headers },
  });
  const datos = await respuesta.json().catch(() => null);
  if (!respuesta.ok) {
    const error = new Error(`HTTP ${respuesta.status}`);
    error.detail = datos?.detail;
    throw error;
  }
  return datos;
}

const parametros = new URLSearchParams({ titulo: "ray", limit: "20", offset: "0" });
const libros = await api(`/libros/?${parametros}`);

const venta = await api("/ventas/", {
  method: "POST",
  body: JSON.stringify({
    cliente_id: 1,
    renglones: [{ libro_id: 1, cantidad: 2 }],
  }),
});
```

Reemplazar los IDs por valores reales y resolver CORS si el frontend usa otro
origen. Crear una venta persiste datos: no ejecutar el ejemplo en producción sin
querer registrar la operación.
