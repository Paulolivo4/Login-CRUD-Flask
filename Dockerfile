FROM python:3.11-slim

# Evitar preguntas interactivas
ENV DEBIAN_FRONTEND=noninteractive

# Instalar dependencias del sistema necesarias para ODBC
RUN apt-get update && apt-get install -y \
    curl \
    gnupg \
    unixodbc \
    unixodbc-dev \
    ca-certificates \
    && rm -rf /var/lib/apt/lists/*

# Agregar la clave de Microsoft
RUN curl -s https://packages.microsoft.com/keys/microsoft.asc | apt-key add -

# Agregar repo oficial de Microsoft para Debian 12 (bookworm)
RUN curl -s https://packages.microsoft.com/config/debian/12/prod.list \
    -o /etc/apt/sources.list.d/mssql-release.list

# Instalar driver ODBC 18
RUN apt-get update && ACCEPT_EULA=Y apt-get install -y msodbcsql18 \
    && rm -rf /var/lib/apt/lists/*

# Crear carpeta de la app
WORKDIR /app

# Copiar requerimientos
COPY requirements.txt .

# Instalar dependencias Python
RUN pip install --no-cache-dir -r requirements.txt

# Copiar el resto de la app
COPY . .

# Puerto default para Render
EXPOSE 10000

# Comando de inicio
CMD gunicorn app:app --bind 0.0.0.0:10000
