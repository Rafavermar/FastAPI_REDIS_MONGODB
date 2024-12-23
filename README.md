# Best Movies API

Este proyecto consiste en el desarrollo de una **API** que maneja información de películas, utilizando **FastAPI** como framework principal. Se integra con **MongoDB** para la persistencia de usuarios y **Redis** para el almacenamiento en caché de datos de películas. La seguridad se implementa mediante **JWT** (OAuth2 con “password flow”) y claves de API. Todo ello se despliega usando **Docker** y **Docker Compose**, asegurando un entorno portable y reproducible.

---

## Contenido

1. [Características Principales](#características-principales)  
2. [Arquitectura](#arquitectura)  
3. [Requisitos](#requisitos)  
4. [Puesta en Marcha](#puesta-en-marcha)  
    1. [Clonar el repositorio](#1-clonar-el-repositorio)  
    2. [Configurar variables de entorno (opcional)](#2-configurar-variables-de-entorno-opcional)  
    3. [Levantar los contenedores con docker-compose](#3-levantar-los-contenedores-con-docker-compose)  
    4. [Explorar la API con Swagger](#4-explorar-la-api-con-swagger)  
    5. [Uso de Postman](#5-uso-de-postman)  
5. [Endpoints Disponibles](#endpoints-disponibles)  
6. [Colección Postman y CSV](#colección-postman-y-csv)  
7. [Notas Adicionales](#notas-adicionales)

---

## Características Principales

- **Registro de usuarios** en MongoDB, validando calificación de contenido (`G`, `PG`, `PG-13`, `R`, `NC-17`) y credenciales.
- **Autenticación** mediante **JWT** (con `grant_type=password`) para solicitar tokens de acceso.
- **Claves de API** para restringir ciertos endpoints.  
- **Películas** cargadas en **Redis** desde un CSV, filtradas inicialmente (en la carga) por ciertas condiciones (`tomatometer_status="Certified-Fresh"`, `content_rating != NR`).
- **Endpoints** para obtener lista de películas filtradas por la calificación de contenido del usuario y para consultar el tamaño de las claves en Redis.
- **Containerización** con Docker y orquestación con docker-compose.

---

## Arquitectura




1. El **contenedor FastAPI** inicia y carga datos en Redis desde un CSV.  
2. MongoDB gestiona el registro y autenticación de usuarios.  
3. Redis almacena la información de películas.  
4. Los usuarios interactúan con la API para registrarse, solicitar tokens y consultar películas.

---

## Requisitos

- **Docker** y **Docker Compose** instalados en tu máquina.  
- Conexión a Internet (si quieres bajar la imagen desde Docker Hub).

---

## Puesta en Marcha

### 1. Clonar el repositorio

```bash
git clone https://github.com/tu-usuario/best-movies-api.git
cd best-movies-api
```



### 2. Configurar variables de entorno (opcional)

El proyecto ya define, en su docker-compose.yml, variables de entorno como API_KEY y SECRET_KEY.
Si deseas cambiarlas, puedes editarlas directamente en docker-compose.yml o agregar un archivo .env.

### 3. Levantar los contenedores con docker-compose
```bash
docker-compose up -d
```
Este comando levantará tres contenedores:
- redis
- mongodb
- act4 (la imagen FastAPI)

**Nota:** El contenedor de FastAPI expone el puerto 4242.

### 4. Explorar la API con Swagger
Una vez que los contenedores estén corriendo:

Abre tu navegador web.

Ve a http://localhost:4242/docs para Swagger UI o a http://localhost:4242/redoc para Redoc.

Podrás ver la documentación interactiva, probar los endpoints y ver las peticiones/ respuestas en tiempo real.

### 5. Uso de Postman
En la carpeta Assets encontrarás la colección de Postman y el entorno necesarios para probar la API.

Importa la colección (FastAPI Movie API.postman_collection.json) en Postman.
Configura las variables de entorno con FastAPI_Movie_API_Collection_ENV.postman_environment.json si lo deseas.

## Endpoints Disponibles
A continuación se describen los endpoints principales:

1. **Registrar Usuario**

- Endpoint: POST /act4/register?api_key=TU_API_KEY
- Descripción: Registra un nuevo usuario.
- Cuerpo de la petición (JSON):
```json
{
  "username": "string", 
  "password": "string",
  "content_rating": "G/PG/PG-13/R/NC-17"
}
```

- Respuestas:
  - 204 No Content: Usuario registrado con éxito.
  - 400: Usuario ya registrado.
  - 422: Error en validación (username o password inválidos, content_rating fuera de rango).
  - 401: API Key no válida.
  
2. **Solicitar Token**

- Endpoint: POST /act4/token
- Descripción: Solicita un token JWT usando OAuth2 (grant type = password).
- Cuerpo de la petición (form-url-encoded):
```makefile
grant_type=password&username=TU_USUARIO&password=TU_PASSWORD
```
- Respuestas:
  - 200 OK: Devuelve access_token.
  - 401: Usuario/contraseña inválidos.
  
3. **Obtener Películas por Calificación**

- Endpoint: GET /act4/movies-by-content-rating
- Descripción: Retorna las 10 películas mejor valoradas (por tomatometer_rating), filtradas por la calificación de contenido del usuario autenticado.
- Auth requerida: Se envía el token JWT en el encabezado Authorization: Bearer <token>.
- Respuestas:
  - 200 OK: Devuelve lista de películas.
  - 401: Token inválido o caducado.
  
4. **Obtener Tamaño de Claves en Redis**

- Endpoint: GET /act4/key-list-size?api_key=TU_API_KEY
- Descripción: Devuelve la cantidad de keys (películas) que hay en Redis.
- Respuestas:
  - 200 OK: Devuelve key_list_size.
  - 401: API Key no válida.

## Colección Postman y CSV
En el directorio Assets se incluyen:

- rotten_tomatoes_movies.csv: Archivo con datos de películas cargado en Redis al iniciar el contenedor.
- FastAPI Movie API.postman_collection.json: Colección para Postman con ejemplos de llamadas a los endpoints.
- FastAPI_Movie_API_Collection_ENV.postman_environment.json: Variables de entorno para Postman.
- 
## Notas Adicionales
Imagen Docker en Docker Hub (opcional):
Si deseas usar directamente la imagen ya compilada, revisa en docker-compose.yml la línea:

```yaml
image: jrvm/eoi-fastapi-act4:v2
```

Puedes cambiarla si quieres usar tu propia imagen.

**Variables de Entorno Importantes:**

- API_KEY: Para los endpoints que requieren ?api_key=
- SECRET_KEY: Para firmar los JWT.
- Versión de Python: 3.9 (definida en el Dockerfile).

Swagger/OpenAPI: disponible en http://localhost:4242/docs.

Redoc: disponible en http://localhost:4242/redoc.