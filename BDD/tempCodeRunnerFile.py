import pyodbc

def get_connection():
    """Crea y devuelve la conexión a Azure SQL Server"""
    try:
        connection = pyodbc.connect(
            "DRIVER={ODBC Driver 18 for SQL Server};"
            "SERVER=ufoodsql.database.windows.net;"
            "DATABASE=UFOOD;"
            "UID=adminsql;"
            "PWD=Chispo11;"
            "Encrypt=yes;"
            "TrustServerCertificate=no;"
            "Connection Timeout=30;"
        )
        print("Conexión exitosa a Azure SQL")
        return connection
    except Exception as ex:
        print("Error al conectar a Azure SQL:", ex)
        return None