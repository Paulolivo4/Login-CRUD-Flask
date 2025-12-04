FROM python:3.11-slim

ENV DEBIAN_FRONTEND=noninteractive

# Instalar dependencias mínimas
RUN apt-get update && apt-get install -y \
    curl \
    gnupg2 \
    ca-certificates \
    unixodbc \
    unixodbc-dev \
    && rm -rf /var/lib/apt/lists/*

# Importar clave pública de Microsoft en el formato correcto
RUN curl -s https://packages.microsoft.com/keys/microsoft.asc \
    | gpg --dearmor \
    | tee /usr/share/keyrings/microsoft.gpg > /dev/null

# Agregar repositorio de Microsoft
RUN echo "deb [arch=amd64 signed-by=/usr/share/keyrings/microsoft.gpg] https://packages.microsoft.com/debian/12/prod bookworm main" \
    > /etc/apt/sources.list.d/mssql-release.list

# Instalar Driver ODBC 18
RUN apt-get update && ACCEPT_EULA=Y apt-get install -y msodbcsql18 \
    && rm -rf /var/lib/apt/lists/*

# Crear carpeta de la app
WORKDIR /app

# Copiar requirements
COPY requirements.txt .

# Instalar dependencias Python
RUN pip install --no-cache-dir -r requirements.txt

# Copiar el resto de la app
COPY . .

# Puerto para Render
EXPOSE 10000

# Comando de inicio (cámbialo si tu app se llama distinto)
CMD ["gunicorn", "app:app", "--bind", "0.0.0.0:10000"]
