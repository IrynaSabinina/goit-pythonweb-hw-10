import logging
from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from starlette.responses import JSONResponse
from slowapi.errors import RateLimitExceeded
from alembic import command
from alembic.config import Config

# Ініціалізація логера для SQLAlchemy та rate limiter
logging.basicConfig()
logging.getLogger("sqlalchemy.engine").setLevel(logging.INFO)

# Логер для відслідковування ліміту запитів
logger = logging.getLogger("rate_limiter")

# Імпортуємо маршрути
from src.api import contacts, utils, users, auth


# Ініціалізація FastAPI додатку
app = FastAPI()

# Додаємо CORS middleware для контролю доступу з інших доменів
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:8000"],  # Дозволяємо запити тільки з цього домену
    allow_credentials=True,
    allow_methods=["*"],  # Дозволяємо всі методи (GET, POST, PUT, DELETE тощо)
    allow_headers=["*"],  # Дозволяємо всі заголовки
)

# Обробник помилок для Rate Limiting, викликається, коли кількість запитів перевищує ліміт
@app.exception_handler(RateLimitExceeded)
async def rate_limit_handler(request: Request, exc: RateLimitExceeded):
    # Логування попередження про перевищення ліміту
    logger.warning(f"Rate limit exceeded for '{request.client.host}' at '{request.url.path}'.")
    # Повертаємо користувачу відповідь з кодом 429 (Too Many Requests)
    return JSONResponse(
        status_code=status.HTTP_429_TOO_MANY_REQUESTS,
        content={"error": "Перевищено ліміт запитів. Спробуйте пізніше."},
    )

# Підключаємо маршрути для різних частин додатку
app.include_router(contacts.router, prefix="/api")
app.include_router(utils.router, prefix="/api")
app.include_router(auth.router, prefix="/api")
app.include_router(users.router, prefix="/api")

# Функція для запуску міграцій за допомогою Alembic
async def run_migrations():
    try:
        alembic_cfg = Config("alembic.ini")  # Шлях до конфігураційного файлу Alembic
        command.upgrade(alembic_cfg, "head")  # Застосовуємо всі міграції до останньої версії
    except Exception as e:
        # Логування помилки, якщо міграції не вдалося застосувати
        logger.error(f"Failed to apply migrations: {e}")
        raise

# Запуск міграцій при старті додатка
@app.on_event("startup")
async def startup_event():
    await run_migrations()  # Викликаємо функцію для застосування міграцій

# Запуск додатка за допомогою uvicorn (якщо файл виконується напряму)
if __name__ == "__main__":
    import uvicorn
    # Запуск сервера на localhost:8000 з опцією перезавантаження коду при зміні
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)
