from Flask import Flask
import pyodbc

config = {}
whith open('DatabaseConfig.txt') as f:
    for line in f:
        key, value = line.strip().split('=')
        config[key.strip()] = value.strip()
        
conn_str =
    f"DRIVER={{{config['driver']}}};"
    f"SERVER={config['server']};"
    f"DATABASE={config['database']};" 
    
conn = pyodbc.connect(conn_str)
cursor = conn.cursor()

cursor.execute("SELECT TOP 1 * FROM LOGINDETAILS")
row = cursor.fetchone()
print(row)