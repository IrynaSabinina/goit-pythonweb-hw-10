from datetime import date, datetime
from typing import Optional, List
from pydantic import BaseModel, Field, ConfigDict, EmailStr, validator
import re

class ContactModel(BaseModel):
    name: str = Field(min_length=2, max_length=50, example="John")
    surname: str = Field(min_length=2, max_length=50, example="Doe")
    email: EmailStr = Field(min_length=7, max_length=100, example="john.doe@example.com")
    phone: str = Field(min_length=7, max_length=20, example="+380501234567")
    birthday: date = Field(example="1990-01-01")
    info: Optional[str] = Field(None, max_length=500, example="Additional info")
    user_id: int = Field(example=1)  # Додано поле user_id

    # Валідація номера телефону
    @validator("phone")
    def validate_phone(cls, value):
        # Перевірка формату номера телефону (наприклад, +380501234567)
        phone_regex = r"^\+?[1-9]\d{1,14}$"  # Міжнародний формат
        if not re.match(phone_regex, value):
            raise ValueError("Phone number must be in international format (e.g., +380501234567)")
        return value

    # Валідація дня народження
    @validator("birthday")
    def validate_birthday(cls, value):
        # Перевірка, що дата народження не в майбутньому
        if value > date.today():
            raise ValueError("Birthday cannot be in the future")
        return value

class ContactResponse(ContactModel):
    id: int
    created_at: datetime
    updated_at: Optional[datetime]
    model_config = ConfigDict(from_attributes=True)  # Підтримка ORM mode

class UserCreate(BaseModel):
    username: str = Field(min_length=3, max_length=50, example="john_doe")  # Додано поле username
    email: EmailStr
    password: str = Field(min_length=6)

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class User(BaseModel):
    id: int
    username: str  # Додано поле username
    email: EmailStr
    is_verified: bool
    avatar_url: Optional[str]
    contacts: List[ContactResponse] = []  # Додано список контактів
    model_config = ConfigDict(from_attributes=True)  # Підтримка ORM mode


class Token(BaseModel):
    """
    Схема для JWT-токена.
    """
    access_token: str  # Токен доступу
    token_type: str = "bearer"  # Тип токена (за замовчуванням "bearer")

class TokenData(BaseModel):
    """
    Схема для даних, які зберігаються в токені.
    """
    email: Optional[str] = None  # Електронна пошта користувача

class RequestEmail(BaseModel):
    """
    Схема для запиту електронної пошти.
    """
    email: EmailStr  # Електронна пошта