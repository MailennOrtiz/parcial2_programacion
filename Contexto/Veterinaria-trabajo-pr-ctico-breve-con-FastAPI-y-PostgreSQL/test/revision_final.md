# Revisión final — 4 de noviembre de 2026

## Resultados

| Comprobación | Resultado |
| --- | --- |
| Suite automatizada | 72 pruebas aprobadas |
| `pip check` | Sin dependencias incompatibles |
| PostgreSQL | Versión 18.4, superior al mínimo 16 |
| C-01 a C-06 | Aprobados con los routers reales y PostgreSQL en un esquema aislado |
| C-07 | Dos SELECT con una y tres prácticas; capturas del usuario transcritas en `evidencia_c07.md` |
| C-08 | UPDATE directo rechazado por CHECK, SQLSTATE 23514; precio original conservado |
| C-09 | HTTP real: salud 200 en 0,005 s, con tres consultas de stock pendientes |

## Regresión sobre PostgreSQL

Se creó un esquema de revisión dentro de una transacción y se cargaron los datos
iniciales. Se usaron los routers de producción mediante ASGI y sesiones unidas a
esa conexión con `join_transaction_mode="create_savepoint"`. Así, los commits y
rollbacks de los services no confirmaron la transacción externa.

Salida de la revisión:

```text
C-01: 422 para parametro no entero.
C-02: 409 para email y nombre de practica repetidos.
C-03: 409 para segunda ficha.
C-04: 409 por referencias inexistentes; rollback completo del turno comprobado.
C-05: duenio 409; turno 204; filas intermedias eliminadas por cascada.
C-06: 201, precios 15000.00/12000.00, total 27000.00, fecha UTC con Z.
Adicionales: PATCH parcial, paginacion invalida y practica repetida comprobados.
Revision PostgreSQL APROBADA. Esquema aislado eliminado por ROLLBACK; datos originales intactos.
```

Al terminar se ejecutó rollback de la transacción externa y se comprobó que el
esquema de revisión ya no existía. No se ejecutó `reiniciar.py` sobre las tablas
originales ni se conservaron los registros de prueba.

## Revisión de Git y secretos

- `.env`, `.venv/` y el `.env` del proyecto de referencia están ignorados por Git.
- No había archivos rastreados al revisar `git ls-files`; los archivos del proyecto
  seguían sin agregar al repositorio. No se creó ningún commit durante la revisión.
- Se analizaron 119 archivos de texto candidatos a entrega con patrones de URLs
  con contraseña, tokens y claves privadas. El único aviso fue revisado manualmente:
  una contraseña de ejemplo en el `env.example` del proyecto anterior, no una
  credencial real. No se modificó el proyecto de referencia.
- Esta revisión no garantiza detectar cualquier secreto: antes del commit hay que
  revisar `git diff --cached` y confirmar que `.env` no esté incluido.

## Antes de entregar

1. Revisar los cambios y agregar al repositorio únicamente los archivos de entrega.
2. Confirmar que `git diff --cached` no contiene credenciales ni entornos virtuales.
3. Crear el commit y subirlo al repositorio de entrega.
4. Conservar las evidencias de C-07, C-08 y C-09 junto con los archivos de prueba.
