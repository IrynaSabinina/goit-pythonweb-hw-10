import logging
from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from starlette.responses import JSONResponse
from slowapi.errors import RateLimitExceeded
from alembic import command
from alembic.config import Config


logging.basicConfig()
logging.getLogger("sqlalchemy.engine").setLevel(logging.INFO)\
# Ініціалізація логера
logger = logging.getLogger("rate_limiter")

# Імпортуємо маршрути
from src.api import contacts, utils, users, auth


app = FastAPI()

# Додаємо CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:8000"],  # Дозволяємо запити з цього домену
    allow_credentials=True,
    allow_methods=["*"],  # Дозволяємо всі методи (GET, POST, PUT, DELETE тощо)
    allow_headers=["*"],  # Дозволяємо всі заголовки
)

# Обробник помилок для Rate Limiting
@app.exception_handler(RateLimitExceeded)
async def rate_limit_handler(request: Request, exc: RateLimitExceeded):
    logger.warning(f"Rate limit exceeded for '{request.client.host}' at '{request.url.path}'.")
    return JSONResponse(
        status_code=status.HTTP_429_TOO_MANY_REQUESTS,
        content={"error": "Перевищено ліміт запитів. Спробуйте пізніше."},
    )

# Підключаємо маршрути
app.include_router(contacts.router, prefix="/api")
app.include_router(utils.router, prefix="/api")
app.include_router(auth.router, prefix="/api")
app.include_router(users.router, prefix="/api")

# Функція для застосування міграцій
async def run_migrations():
    try:
        alembic_cfg = Config("alembic.ini")
        command.upgrade(alembic_cfg, "head")
    except Exception as e:
        logger.error(f"Failed to apply migrations: {e}")
        raise

# Запуск міграцій при старті додатка
@app.on_event("startup")
async def startup_event():
    await run_migrations()

if __name__ == "__main__":
    import uvicorn

    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)