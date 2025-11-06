# Usa una imagen base de Python con Alpine para ser ligera
FROM python:3.10-alpine

# Define el directorio de trabajo dentro del contenedor
WORKDIR /app

# Instala dependencias necesarias para psycopg2-binary
RUN apk update && apk add postgresql-dev gcc python3-dev musl-dev

# Copia e instala las dependencias de Python
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copia el resto de la aplicación (incluyendo app.py y templates/)
COPY . .

# Comando para correr la aplicación
CMD ["python", "app.py"]