import logging
from sqlalchemy.ext.asyncio import AsyncSession

from src.repository.users import UserRepository
from src.schemas import UserCreate, User

logger = logging.getLogger("rate_limiter")

class UserService:
    def __init__(self, db: AsyncSession):
        self.repository = UserRepository(db)

    async def create_user(self, user: UserCreate, avatar_url: str = None) -> User:
        """
        Створення нового користувача в базі даних
        """
        logger.info("Creating user in service: %s", user.dict())
        try:
            return await self.repository.create_user(user, avatar_url)
        except Exception as e:
            logger.error("Error in UserService.create_user: %s", str(e))
            raise

    async def get_user_by_id(self, user_id: int) -> User | None:
        """
        Отримання користувача за ID
        """
        return await self.repository.get_user_by_id(user_id)

    async def get_user_by_username(self, username: str) -> User | None:
        """
        Отримання користувача за іменем користувача
        """
        return await self.repository.get_user_by_username(username)

    async def get_user_by_email(self, email: str) -> User | None:
        """
        Отримання користувача за електронною поштою
        """
        return await self.repository.get_user_by_email(email)

    async def update_avatar(self, user_id: int, avatar_url: str) -> User:
        """
        Оновлення аватара користувача
        """
        user = await self.repository.get_user_by_id(user_id)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
            )
        return await self.repository.update_avatar_url(user.email, avatar_url)

    async def confirm_email(self, email: str) -> None:
        """
        Підтвердження електронної пошти користувача
        """
        user = await self.repository.get_user_by_email(email)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
            )
        await self.repository.confirmed_email(email)
