# Usamos una imagen base de Python
FROM python:3.9-slim

# Establecer el directorio de trabajo
WORKDIR /app

# Copiar el archivo requirements.txt en el contenedor
COPY requirements.txt .

# Instalar las dependencias desde requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Copiar el resto del código de la aplicación en el contenedor
COPY . /app

# Copiar el archivo CSV dentro del contenedor
COPY data/rotten_tomatoes_movies.csv /app

# Exponer el puerto 4242 (ya que quieres que FastAPI escuche en este puerto)
EXPOSE 4242

# Comando para ejecutar la aplicación FastAPI con Uvicorn en el puerto 4242
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "4242"]
