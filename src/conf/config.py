from pydantic_settings import BaseSettings  # Оновлений імпорт
from pydantic import ConfigDict, EmailStr

class Settings(BaseSettings):
    # Database
    DB_NAME: str
    DB_USER: str
    DB_PASSWORD: str
    DB_HOST: str
    DB_PORT: str

    # JWT
    JWT_SECRET: str
    JWT_ALGORITHM: str = "HS256"
    JWT_EXPIRATION_SECONDS: int = 3600
    JWT_REFRESH_EXPIRATION_SECONDS: int

    # Cloudinary
    CLOUDINARY_CLOUD_NAME: str
    CLOUDINARY_API_KEY: str
    CLOUDINARY_API_SECRET: str

    # Email
    MAIL_USERNAME: EmailStr
    MAIL_PASSWORD: str
    MAIL_FROM: EmailStr
    MAIL_PORT: int
    MAIL_SERVER: str
    MAIL_FROM_NAME: str = "API Service"
    MAIL_STARTTLS: bool = False
    MAIL_SSL_TLS: bool = True
    USE_CREDENTIALS: bool = True
    VALIDATE_CERTS: bool = True

    @property
    def database_url(self) -> str:
        """Формує URL для підключення до PostgreSQL."""
        return f"postgresql://{self.DB_USER}:{self.DB_PASSWORD}@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"

    # Конфігурація
    model_config = ConfigDict(
        extra="ignore",  # Ігноруємо змінні, які не визначені у класі
        env_file=".env",
        # Використовуємо .env файл для завантаження змінних
        env_file_encoding="utf-8",  # Кодування .env файлу
        case_sensitive=True  # Урахування регістру для змінних
    )

settings = Settings()