from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from src.repository.contacts import ContactRepository
from src.schemas import ContactModel
from src.database.models import User


class ContactService:
    def __init__(self, db: AsyncSession):
        # Initialize with the database session and the contact repository
        self.repository = ContactRepository(db)

    async def create_contact(self, body: ContactModel, user: User):
        """
        Creates a new contact for a specific user.
        Checks if a contact with the same email or phone already exists.
        """
        # Check if contact already exists for the user with the provided email or phone
        if await self.repository.is_contact_exists(body.email, body.phone, user):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Contact with '{body.email}' email or '{body.phone}' phone number already exists.",
            )
        # Create the new contact
        return await self.repository.create_contact(body, user)

    async def get_contacts(
        self, name: str, surname: str, email: str, skip: int, limit: int, user: User
    ):
        """
        Retrieves a list of contacts for a specific user with filtering options.
        Supports pagination using skip and limit.
        """
        return await self.repository.get_contacts(name, surname, email, skip, limit, user)

    async def get_contact(self, contact_id: int, user: User):
        """
        Retrieves a specific contact by ID for the user.
        """
        # Fetch contact by ID
        contact = await self.repository.get_contact_by_id(contact_id, user)
        if contact is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Contact not found",
            )
        return contact

    async def update_contact(self, contact_id: int, body: ContactModel, user: User):
        """
        Updates a contact by ID for a specific user.
        """
        # Attempt to update the contact
        updated_contact = await self.repository.update_contact(contact_id, body, user)
        if updated_contact is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Contact not found",
            )
        return updated_contact

    async def remove_contact(self, contact_id: int, user: User):
        """
        Deletes a contact by ID for a specific user.
        """
        # Attempt to remove the contact
        deleted_contact = await self.repository.remove_contact(contact_id, user)
        if deleted_contact is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Contact not found",
            )
        return deleted_contact

    async def get_upcoming_birthdays(self, days: int, user: User):
        """
        Retrieves a list of contacts with upcoming birthdays within the next `days` days for a specific user.
        """
        return await self.repository.get_upcoming_birthdays(days, user)
