import pyodbc

def get_connection():
    """Crea y devuelve la conexión a SQL Server"""
    try:
        connection = pyodbc.connect(
            "DRIVER={ODBC Driver 17 for SQL Server};"
            "SERVER=DESKTOP-U5C95MQ\MSSQLSERVER01;"
            "DATABASE=LOGINDB;"
            "Trusted_Connection=yes;"  # Si usas autenticación de Windows
        )
        return connection
    except Exception as ex:
        print("Error al conectar a la base de datos:", ex)
        return None
