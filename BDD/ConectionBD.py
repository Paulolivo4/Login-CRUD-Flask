from flask import Flask
import pyodbc

# Leer configuración del archivo
config = {}
with open('DatabaseConfig.txt', 'r') as f:
    for line in f:
        if '=' in line:
            key, value = line.strip().split('=', 1)
            config[key] = value
conn_str = f"DRIVER={config['driver']};SERVER={config['server']};DATABASE={config['database']};Trusted_Connection=yes;"
    
conn = pyodbc.connect(conn_str)
cursor = conn.cursor()

cursor.execute("SELECT TOP 1 * FROM LOGINDETAILS")
row = cursor.fetchone()
print(row)

