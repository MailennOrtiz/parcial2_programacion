# Pruebas del ejercicio 3

Las pruebas automatizadas usan una base SQLite en memoria independiente; no leen
el `.env` ni modifican PostgreSQL. Desde la raíz del proyecto:

```powershell
python -m pip install -r requirements-dev.txt
python -m unittest discover -s test -p "test_*.py" -v
```

`03_contratos_crud.http` contiene casos manuales para REST Client contra una API
en ejecución y una base PostgreSQL dedicada de prueba. El archivo inserta datos;
no debe ejecutarse sobre una base que se quiera mantener intacta. Ajustá la URL
si corresponde. Las pruebas con SQLite no demuestran el comportamiento específico
de PostgreSQL ni reemplazan los casos completos de entrega del parcial.

`04_ventas_y_conflictos.http` agrega casos de perfiles, referencias inexistentes
y venta con dos renglones. Inserta datos y utiliza nombres únicos fijos: ejecutarlo
en una base de prueba apropiada, y no asumir que se puede repetir sin cambiar datos.
