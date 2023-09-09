from pydantic import BaseModel, Field, EmailStr

class UserLoginSchema(BaseModel):
    email: EmailStr = Field(...)
    password: str = Field(...)

    class Config:
        json_schema_extra = {
            "example": {
                "email": "john@me.com",
                "password": "12345678"
            }
        }

class UserSchema(BaseModel):
    email: EmailStr = Field(...)
    password: str = Field(...)

    class Config:
        json_schema_extra = {
            "example": {
                "email": "john@me.com",
                "password": "12345678"
            }
        }