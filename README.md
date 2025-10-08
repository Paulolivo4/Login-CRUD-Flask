# LOGIN-FLASK

Proyecto Flask para login. Instrucciones rápidas para preparar el entorno virtual en Windows (PowerShell).

1) Crear el entorno virtual (si no está creado):

```powershell
python -m venv .venv
```

2) Activar el entorno virtual:

```powershell
.\.venv\Scripts\Activate.ps1
```

3) Actualizar pip e instalar dependencias desde `requirements.txt`:

```powershell
python -m pip install --upgrade pip
pip install -r requirements.txt
```

4) Ejecutar la aplicación:

```powershell
python app.py
```

Notas:
- `pyodbc` requiere los drivers ODBC de SQL Server en Windows (p. ej. "ODBC Driver 17 for SQL Server").
- He añadido `.venv` localmente y generado `requirements.txt` con Flask y pyodbc.