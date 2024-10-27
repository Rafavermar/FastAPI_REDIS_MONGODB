from pydantic import BaseModel, field_validator
from fastapi import HTTPException


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


class UserLogin(BaseModel):
    username: str
    password: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str
