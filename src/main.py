import redis
from db import get_users_collection
from fastapi import Depends, HTTPException, Security, Response
from fastapi import APIRouter
from auth import create_access_token, verify_password, hash_password, verify_api_key, api_key_query
from models import UserRegister, TokenResponse, MoviesResponse, Movie
from datetime import timedelta
from fastapi.security import OAuth2PasswordRequestForm
from fastapi import Request
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from fastapi import FastAPI
from contextlib import asynccontextmanager
from load_data import load_movies
import os
from typing import cast
from starlette.datastructures import State


SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = "HS512"


def get_redis_client(request: Request):
    return request.app.state.redis_client


@asynccontextmanager
async def lifespan(_):
    app.state.redis_client = redis.Redis(host='redis', port=6379, db=0)
    # Usar cast para indicar el tipo de app.state
    app.state = cast(State, app.state)
    # Cargar las películas en Redis al iniciar la aplicación
    load_movies(app.state.redis_client)
    yield
    # Cerrar la conexión de Redis al finalizar
    app.state.redis_client.close()


# Inicializamos FastAPI con el lifespan
app = FastAPI(lifespan=lifespan)

# Router "best-movies"
router = APIRouter(
    prefix="/act4",
    tags=["best-movies"]
)


# Ruta para registrar usuarios
@router.post(
    "/register",
    description="Registra un nuevo usuario con su nombre de usuario, contraseña y calificación de contenido. **Solo se aceptan las calificaciones de contenido siguientes**: G, PG, PG-13, R, NC-17.",
    summary="Registrar nuevo usuario",
    response_description="Usuario registrado exitosamente.",
    responses={
        400: {"description": "El usuario ya está registrado o contenido rating inválido"},
        401: {"description": "No autorizado. Api key no válida"},
        422: {"description": "Error de validación en username/password"}
    },
    status_code=204
)
async def register_user(user: UserRegister, api_key: str = Security(api_key_query),
                        users_collection=Depends(get_users_collection)):
    verify_api_key(api_key)  # Verifica si la API Key es válida

    allowed_ratings = ["G", "PG", "PG-13", "R", "NC-17"]
    if user.content_rating not in allowed_ratings:
        raise HTTPException(status_code=422, detail="Calificación de contenido inválida.")

    hashed_password = hash_password(user.password)
    user_data = {
        "username": user.username,
        "hashed_password": hashed_password,
        "content_rating": user.content_rating
    }

    if users_collection.find_one({"username": user.username}):
        raise HTTPException(status_code=400, detail="El usuario ya está registrado")

    users_collection.insert_one(user_data)
    return {"message": "Usuario registrado correctamente"}


# Ruta para solicitar token (JWT)
@router.post(
    "/token",
    response_model=TokenResponse,
    summary="Solicitar Token JWT",
    description="Solicita un token de acceso (JWT) utilizando credenciales de usuario.",
    response_description="Devuelve un token JWT válido por 15 minutos.",
    responses={
        401: {"description": "Usuario no registrado o contraseña errónea"},
    },
    status_code=200
)
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends(),
                                 users_collection=Depends(get_users_collection)):
    # Buscar el usuario en la base de datos
    db_user = users_collection.find_one({"username": form_data.username})
    if not db_user or not verify_password(form_data.password, db_user["hashed_password"]):
        raise HTTPException(status_code=401, detail="Usuario no registrado o contraseña errónea")

    # Crear un token de acceso JWT
    access_token_expires = timedelta(minutes=15)
    access_token = create_access_token(
        data={"sub": db_user["username"], "cr": db_user["content_rating"]},
        expires_delta=access_token_expires
    )

    return {"access_token": access_token, "token_type": "bearer"}


# Ruta para obtener películas por content rating
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="act4/token")


@router.get(
    "/movies-by-content-rating",
    response_model=MoviesResponse,
    summary="Obtener películas por calificación",
    description="Devuelve una lista de las 10 películas mejor valoradas, filtradas por la calificación de contenido del usuario autenticado.",
    response_description="Lista de películas filtradas.",
    responses={
        200: {"description": "Lista de películas encontradas", "content": {"application/json": {"example": [
            {"movie_title": "Inception", "original_release_date": "2010-07-16", "genres": ["Action", "Sci-Fi"],
             "content_rating": "PG-13", "tomatometer_rating": 87}]}}},
        401: {"description": "Token inválido o no autorizado", "headers": {"WWW-Authenticate": {"schema": "Bearer"}}}
    },
    status_code=200
)
async def get_movies_by_content_rating(
        response: Response,
        token: str = Depends(oauth2_scheme),
        redis_client=Depends(get_redis_client)
):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        content_rating = payload.get("cr")
        if content_rating is None:
            raise HTTPException(status_code=401, detail="Token inválido")

        # Filtrar y obtener películas
        movies = []
        for key in redis_client.scan_iter():
            movie = eval(redis_client.get(key))

            # Aquí parseamos "genres". Suponiendo que en el CSV está separado por comas:
            genres_array = [g.strip() for g in movie["genres"].split(",")]

            if movie['content_rating'] == content_rating:
                movies.append(Movie(
                    movie_title=movie["movie_title"],
                    original_release_date=movie["original_release_date"],
                    genres=genres_array,
                    content_rating=movie["content_rating"],
                    tomatometer_rating=int(movie["tomatometer_rating"])
                ))

        # Ordenar por tomatometer_rating y devolver las 10 mejores
        movies = sorted(movies, key=lambda x: x.tomatometer_rating, reverse=True)[:10]

        return MoviesResponse(movies=movies)

    except JWTError:
        # En caso de error de JWT, devolver 401 con la cabecera "WWW-Authenticate"
        response.headers["WWW-Authenticate"] = "Bearer"
        raise HTTPException(status_code=401, detail="Token inválido")


# Ruta para obtener el número de claves en Redis
@router.get(
    "/key-list-size",
    summary="Obtener tamaño de lista de claves en Redis",
    description="Devuelve el número de claves almacenadas en Redis.",
    response_description="Número total de claves en Redis.",
    responses={
        200: {"description": "Número de claves en Redis",
              "content": {"application/json": {"example": {"key_list_size": 42}}}},
        401: {"description": "API Key no válida"}
    },
    status_code=200
)
async def key_list_size(response: Response, api_key: str = Security(api_key_query),
                        redis_client=Depends(get_redis_client)):
    try:
        verify_api_key(api_key)  # Verificar si la API Key es válida
        num_keys = redis_client.dbsize()
        return {"key_list_size": num_keys}
    except HTTPException:
        # Responder con 401 si la API Key es inválida
        response.headers["WWW-Authenticate"] = "Bearer"
        raise HTTPException(status_code=401, detail="API Key no válida")


app.include_router(router)
