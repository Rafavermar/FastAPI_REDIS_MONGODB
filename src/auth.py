import os
from passlib.context import CryptContext
from jose import jwt
from datetime import datetime, timedelta
from fastapi import HTTPException
from fastapi.security import APIKeyQuery
from starlette.status import HTTP_401_UNAUTHORIZED

# Obtener configuraciones desde variables de entorno
SECRET_KEY = os.getenv("SECRET_KEY")  # Leer desde variable de entorno
ALGORITHM = "HS512"
ACCESS_TOKEN_EXPIRE_MINUTES = 15
API_KEY = os.getenv("API_KEY")  # Leer desde variable de entorno

# Security para API Key
api_key_query = APIKeyQuery(name="api_key", auto_error=False)

# Configuración para hashear contraseñas
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


# Función para crear un token JWT
def create_access_token(data: dict, expires_delta: timedelta):
    to_encode = data.copy()
    expire = datetime.utcnow() + expires_delta
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)


# Función para verificar contraseñas
def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)


def hash_password(password: str):
    return pwd_context.hash(password)


# Verificación de la API Key
def verify_api_key(api_key: str):
    if api_key != API_KEY:
        raise HTTPException(
            status_code=HTTP_401_UNAUTHORIZED, detail="Invalid API Key"
        )
