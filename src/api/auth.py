import logging
from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, BackgroundTasks, Request
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession

from src.database.database import get_db
from src.schemas import UserCreate, User, UserLogin, Token, RequestEmail
from src.services.users import UserService
from src.services.auth import get_current_user, Hash, create_access_token, get_email_from_token
from src.services.uploadfile import UploadFileService
from src.services.email import send_email
from src.conf.config import settings

logger = logging.getLogger("rate_limiter")

router = APIRouter(prefix="/auth", tags=["auth"])

@router.post("/register", response_model=User, status_code=status.HTTP_201_CREATED)
async def register_user(
    user: UserCreate,
    background_tasks: BackgroundTasks,
    request: Request,
    db: AsyncSession = Depends(get_db),
):
    logger.info("Received registration request: %s", user.dict())
    service = UserService(db)
    print("Received request:", user)
    try:
        # Перевірка, чи існує користувач з таким email
        existing_user_by_email = await service.get_user_by_email(user.email)
        if existing_user_by_email:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Користувач з таким email вже існує",
            )

        # Перевірка, чи існує користувач з таким іменем
        existing_user_by_username = await service.get_user_by_username(user.username)
        if existing_user_by_username:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Користувач з таким іменем вже існує",
            )

        # Хешування пароля
        user.password = Hash().get_password_hash(user.password)
        logger.info("Password hashed successfully")

        # Створення нового користувача
        new_user = await service.create_user(user)
        logger.info("User created successfully: %s", new_user.email)

        # Відправка листа з підтвердженням електронної пошти
        background_tasks.add_task(
            send_email, new_user.email, new_user.username, request.base_url
        )
        return new_user
    except Exception as e:
        logger.error("Error in register_user: %s", str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error",
        )
@router.post("/login", response_model=Token)
async def login_user(
        form_data: OAuth2PasswordRequestForm = Depends(),
        db: AsyncSession = Depends(get_db)
):
    service = UserService(db)
    db_user = await  service.get_user_by_username(form_data.username)

    # Перевірка, чи існує користувач і чи співпадає пароль
    if not db_user or not Hash().verify_password(form_data.password, db_user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Неправильний логін або пароль",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Перевірка, чи підтверджена електронна пошта
    if not db_user.is_verified:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Електронна пошта не підтверджена",
        )

    # Генерація токена доступу
    access_token = await create_access_token(data={"sub": db_user.username})
    return {"access_token": access_token, "token_type": "bearer"}


@router.get("/confirmed_email/{token}")
async def confirmed_email(
    token: str,
    db: AsyncSession = Depends(get_db),
):
    email = await get_email_from_token(token)
    service = UserService(db)
    user = await service.get_user_by_email(email)

    if user is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Помилка верифікації",
        )

    if user.is_verified:
        return {"message": "Ваша електронна пошта вже підтверджена"}

    await service.confirm_email(email)
    return {"message": "Електронну пошту підтверджено"}

@router.post("/request_email")
async def request_email(
    body: RequestEmail,
    background_tasks: BackgroundTasks,
    request: Request,
    db: AsyncSession = Depends(get_db),
):
    service = UserService(db)
    user = await service.get_user_by_email(body.email)

    if user and user.is_verified:
        return {"message": "Ваша електронна пошта вже підтверджена"}

    if user:
        background_tasks.add_task(
            send_email, user.email, user.username, request.base_url
        )

    return {"message": "Перевірте свою електронну пошту для підтвердження"}