import os

import pyodbc


def _connection_string():
    """Build the SQL Server connection string from environment variables.

    DB_CONNECTION_STRING overrides everything. Otherwise DB_SERVER, DB_NAME and
    DB_DRIVER are used, with SQL authentication when DB_USER and DB_PASSWORD are
    set and Windows authentication (trusted connection) when they are not.
    """
    full = os.environ.get('DB_CONNECTION_STRING')
    if full:
        return full

    parts = [
        f"DRIVER={{{os.environ.get('DB_DRIVER', 'ODBC Driver 17 for SQL Server')}}}",
        f"SERVER={os.environ.get('DB_SERVER', 'localhost')}",
        f"DATABASE={os.environ.get('DB_NAME', 'LOGINDB')}",
    ]
    user = os.environ.get('DB_USER')
    password = os.environ.get('DB_PASSWORD')
    if user and password:
        parts += [f"UID={user}", f"PWD={password}"]
    else:
        parts.append("Trusted_Connection=yes")
    return ";".join(parts) + ";"


def get_connection():
    """Create and return the SQL Server connection (None if it fails)."""
    try:
        return pyodbc.connect(_connection_string())
    except Exception as ex:
        print("Error connecting to the database:", ex)
        return None