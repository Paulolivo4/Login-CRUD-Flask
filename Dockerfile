# Imagen base de Python
FROM python:3.11-slim

# Instalar dependencias del sistema y ODBC Driver 18
RUN apt-get update && apt-get install -y \
    curl \
    gnupg \
    unixodbc \
    unixodbc-dev \
    apt-transport-https \
    software-properties-common

# Importar la clave y repositorio oficial de Microsoft
RUN curl https://packages.microsoft.com/keys/microsoft.asc | apt-key add -
RUN curl https://packages.microsoft.com/config/debian/12/prod.list \
    -o /etc/apt/sources.list.d/mssql-release.list

# Instalar el driver ODBC 18
RUN apt-get update && ACCEPT_EULA=Y apt-get install -y msodbcsql18

# Crear carpeta de la app
WORKDIR /app

# Copiar requirements.txt
COPY requirements.txt .

# Instalar dependencias Python
RUN pip install --no-cache-dir -r requirements.txt

# Copiar el resto del proyecto
COPY . . 

# Puerto por defecto de Render
EXPOSE 10000

# Comando para ejecutar Flask con gunicorn
CMD gunicorn app:app --bind 0.0.0.0:10000
