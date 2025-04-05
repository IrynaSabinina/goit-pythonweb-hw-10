from fastapi import APIRouter, Depends, HTTPException, Query, status
from typing import List
from sqlalchemy.ext.asyncio import AsyncSession

from src.schemas import ContactModel, ContactResponse
from src.database.database import get_db
from src.services.contacts import ContactService
from src.services.auth import get_current_user
from src.database.models import User

router = APIRouter(prefix="/contacts", tags=["contacts"])


@router.post("/", response_model=ContactResponse, status_code=status.HTTP_201_CREATED)
async def create_contact(
    body: ContactModel,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    """
    Створює новий контакт для поточного користувача.
    """
    service = ContactService(db)
    return await service.create_contact(body, user)


@router.get("/", response_model=List[ContactResponse])
async def read_contacts(
    name: str = Query(None),
    surname: str = Query(None),
    email: str = Query(None),
    skip: int = 0,
    limit: int = 10,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    """
    Отримує список контактів для поточного користувача з можливістю фільтрації.
    """
    service = ContactService(db)
    return await service.get_contacts(name, surname, email, skip, limit, user)


@router.get("/{contact_id}", response_model=ContactResponse)
async def read_contact(
    contact_id: int,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    """
    Отримує контакт за ID для поточного користувача.
    """
    service = ContactService(db)
    contact = await service.get_contact(contact_id, user)
    if contact is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Contact not found"
        )
    return contact


@router.put("/{contact_id}", response_model=ContactResponse)
async def update_contact(
    contact_id: int,
    body: ContactModel,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    """
    Оновлює контакт за ID для поточного користувача.
    """
    service = ContactService(db)
    contact = await service.update_contact(contact_id, body, user)
    if contact is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Contact not found"
        )
    return contact


@router.delete("/{contact_id}", response_model=ContactResponse)
async def delete_contact(
    contact_id: int,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    """
    Видаляє контакт за ID для поточного користувача.
    """
    service = ContactService(db)
    contact = await service.remove_contact(contact_id, user)
    if contact is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Contact not found"
        )
    return contact


@router.get("/birthdays/", response_model=List[ContactResponse])
async def upcoming_birthdays(
    days: int = Query(default=7, ge=1),
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    """
    Отримує список контактів з днями народження, які настануть протягом наступних `days` днів, для поточного користувача.
    """
    service = ContactService(db)
    return await service.get_upcoming_birthdays(days, user)