from datetime import datetime, timedelta, timezone
from typing import Optional
from fastapi import Depends, HTTPException, status
from passlib.context import CryptContext
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.ext.asyncio import AsyncSession
from jose import JWTError, jwt

# Importing necessary components from the database and configuration
from src.database.database import get_db
from src.conf.config import settings
from src.services.users import UserService


# Hash class to handle password hashing and verification using bcrypt
class Hash:
    # Define the CryptContext for password hashing (bcrypt)
    pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

    # Method to verify a plain password against a hashed password
    def verify_password(self, plain_password, hashed_password):
        return self.pwd_context.verify(plain_password, hashed_password)

    # Method to hash a password
    def get_password_hash(self, password: str):
        return self.pwd_context.hash(password)


# OAuth2PasswordBearer is used to handle token authentication in FastAPI
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/login")


# Function to create an access token for a user
async def create_access_token(data: dict, expires_delta: Optional[int] = None):
    """
    Creates an access JWT token with an optional expiration time.
    If no expiration time is provided, it uses a default value from settings.
    """
    to_encode = data.copy()

    # Calculate expiration time based on provided or default value
    if expires_delta:
        expire = datetime.now(timezone.utc) + timedelta(seconds=expires_delta)
    else:
        expire = datetime.now(timezone.utc) + timedelta(seconds=settings.JWT_EXPIRATION_SECONDS)
    
    # Add the expiration time to the data dictionary
    to_encode.update({"exp": expire})
    
    # Encode the JWT token with the secret key and algorithm from settings
    encoded_jwt = jwt.encode(to_encode, settings.JWT_SECRET, algorithm=settings.JWT_ALGORITHM)
    
    return encoded_jwt


# Dependency function to get the current authenticated user from the token
async def get_current_user(token: str = Depends(oauth2_scheme), db: AsyncSession = Depends(get_db)):
    """
    Decodes the provided JWT token, validates the user, and returns the user object.
    Raises HTTP 401 error if the token is invalid or the user does not exist.
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        # Decode the JWT token to get user data (username in this case)
        payload = jwt.decode(token, settings.JWT_SECRET, algorithms=[settings.JWT_ALGORITHM])
        username = payload["sub"]

        # If no username is found, raise an exception
        if username is None:
            raise credentials_exception
    except JWTError:
        # If there is an error decoding the token, raise an exception
        raise credentials_exception
    
    # Fetch the user from the database using the UserService
    user_service = UserService(db)
    user = await user_service.get_user_by_username(username)

    # If the user is not found in the database, raise an exception
    if user is None:
        raise credentials_exception
    
    return user


# Function to create an email verification token
def create_email_token(data: dict):
    """
    Creates a JWT token for email verification with a 7-day expiration.
    """
    to_encode = data.copy()

    # Set the expiration time for the email verification token (7 days)
    expire = datetime.now(timezone.utc) + timedelta(days=7)
    
    # Add the issued at (iat) and expiration time (exp) to the token
    to_encode.update({"iat": datetime.now(timezone.utc), "exp": expire})
    
    # Encode the token with the secret key and algorithm
    token = jwt.encode(to_encode, settings.JWT_SECRET, algorithm=settings.JWT_ALGORITHM)
    
    return token


# Function to extract the email from the email verification token
async def get_email_from_token(token: str):
    """
    Decodes the email verification token and retrieves the email address.
    Raises an HTTP exception if the token is invalid or cannot be decoded.
    """
    try:
        # Decode the JWT token to extract the email
        payload = jwt.decode(token, settings.JWT_SECRET, algorithms=[settings.JWT_ALGORITHM])
        email = payload["sub"]
        return email
    except JWTError:
        # If the token is invalid or expired, raise an exception
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Неправильний токен для перевірки електронної пошти",
        )
