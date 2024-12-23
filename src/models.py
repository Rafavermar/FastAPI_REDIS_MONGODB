from pydantic import BaseModel, field_validator
from fastapi import HTTPException
from typing import List


class UserRegister(BaseModel):
    username: str
    password: str
    content_rating: str

    @field_validator("content_rating")
    def validate_content_rating(cls, value):
        allowed_ratings = ["G", "PG", "PG-13", "R", "NC-17"]
        if value not in allowed_ratings:
            raise HTTPException(status_code=400, detail=f"Invalid content rating: {value}")
        return value

    @field_validator("username")
    def validate_username_starts_with_uppercase(cls, value):
        if not value[0].isupper():
            raise HTTPException(
                status_code=422,
                detail="El username debe comenzar con una letra mayúscula"
            )
        return value

    @field_validator("password")
    def validate_password_length(cls, value):
        if len(value) < 8:
            raise HTTPException(
                status_code=422,
                detail="La contraseña debe tener al menos 8 caracteres"
            )
        return value


class Movie(BaseModel):
    movie_title: str
    original_release_date: str
    genres: List[str]
    content_rating: str
    tomatometer_rating: int


class MoviesResponse(BaseModel):
    movies: List[Movie]


class UserLogin(BaseModel):
    username: str
    password: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str
