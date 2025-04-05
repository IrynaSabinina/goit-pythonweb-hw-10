from datetime import date, timedelta
from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, or_, func

from src.database.models import Contact, User
from src.schemas import ContactModel


class ContactRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def is_contact_exists(self, email: str, phone: str, user: User) -> bool:
        """
        Перевіряє, чи існує контакт з таким email або phone для конкретного користувача.
        """
        result = await self.db.execute(
            select(Contact).filter(
                and_(
                    or_(Contact.email == email, Contact.phone == phone),
                    Contact.user_id == user.id,
                )
            )
        )
        return result.scalar_one_or_none() is not None

    async def create_contact(self, body: ContactModel, user: User) -> Contact:
        """
        Створює новий контакт для конкретного користувача.
        """
        db_contact = Contact(**body.model_dump(exclude_unset=True), user=user)
        self.db.add(db_contact)
        await self.db.commit()
        await self.db.refresh(db_contact)
        return db_contact

    async def get_contacts(
        self, name: str, surname: str, email: str, skip: int, limit: int, user: User
    ) -> List[Contact]:
        """
        Отримує список контактів для конкретного користувача з можливістю фільтрації.
        """
        query = select(Contact).filter_by(user=user)
        if name:
            query = query.filter(Contact.name.contains(name))
        if surname:
            query = query.filter(Contact.surname.contains(surname))
        if email:
            query = query.filter(Contact.email.contains(email))
        result = await self.db.execute(query.offset(skip).limit(limit))
        return result.scalars().all()

    async def get_contact_by_id(self, contact_id: int, user: User) -> Optional[Contact]:
        """
        Отримує контакт за ID для конкретного користувача.
        """
        result = await self.db.execute(
            select(Contact).filter(and_(Contact.id == contact_id, Contact.user_id == user.id))
        )
        return result.scalar_one_or_none()

    async def update_contact(
        self, contact_id: int, body: ContactModel, user: User
    ) -> Optional[Contact]:
        """
        Оновлює контакт за ID для конкретного користувача.
        """
        db_contact = await self.get_contact_by_id(contact_id, user)
        if db_contact:
            for key, value in body.model_dump(exclude_unset=True).items():
                setattr(db_contact, key, value)
            await self.db.commit()
            await self.db.refresh(db_contact)
        return db_contact

    async def remove_contact(self, contact_id: int, user: User) -> Optional[Contact]:
        """
        Видаляє контакт за ID для конкретного користувача.
        """
        db_contact = await self.get_contact_by_id(contact_id, user)
        if db_contact:
            await self.db.delete(db_contact)
            await self.db.commit()
        return db_contact

    async def get_upcoming_birthdays(self, days: int, user: User) -> List[Contact]:
        """
        Отримує список контактів з днями народження, які настануть протягом наступних `days` днів, для конкретного користувача.
        """
        today = date.today()
        end_date = today + timedelta(days=days)

        query = (
            select(Contact)
            .filter_by(user=user)
            .where(
                or_(
                    func.date_part("day", Contact.birthday).between(
                        func.date_part("day", today), func.date_part("day", end_date)
                    ),
                    and_(
                        func.date_part("day", end_date) < func.date_part("day", today),
                        or_(
                            func.date_part("day", Contact.birthday)
                            >= func.date_part("day", today),
                            func.date_part("day", Contact.birthday)
                            <= func.date_part("day", end_date),
                        ),
                    ),
                )
            )
            .order_by(func.date_part("day", Contact.birthday).asc())
        )

        result = await self.db.execute(query)
        return result.scalars().all()