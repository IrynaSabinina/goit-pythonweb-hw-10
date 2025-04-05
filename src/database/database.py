
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from src.conf.config import settings

# Асинхронний URL для підключення до PostgreSQL
SQLALCHEMY_DATABASE_URL = settings.database_url.replace("postgresql://", "postgresql+asyncpg://")

# Асинхронний двигун
engine = create_async_engine(SQLALCHEMY_DATABASE_URL, echo=True)

# Асинхронна сесія
AsyncSessionLocal = sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
)

Base = declarative_base()

# Залежність для отримання асинхронної сесії
async def get_db() -> AsyncSession:
    async with AsyncSessionLocal() as session:
        yield session
