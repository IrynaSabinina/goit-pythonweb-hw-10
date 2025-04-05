from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text

from src.database.database import get_db

router = APIRouter(tags=["utils"])

@router.get("/healthchecker")
async def healthchecker(db: AsyncSession = Depends(get_db)):
    try:
        # Виконуємо простий SQL-запит для перевірки підключення до бази даних
        result = await db.execute(text("SELECT 1"))
        result = result.scalar_one_or_none()

        # Якщо результат запиту не є очікуваним, викликаємо помилку
        if result is None:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Database is not configured correctly",
            )

        # Якщо все добре, повертаємо повідомлення про успішну перевірку
        return {"message": "Welcome to FastAPI!"}
    except Exception as e:
        # Логуємо помилку (для зручності налагодження)
        print(e)
        # Викликаємо помилку, якщо щось пішло не так
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error connecting to the database",
        )