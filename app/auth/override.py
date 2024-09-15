from fastapi import Request
from fastapi.security import OAuth2PasswordRequestForm
from fastapi_users import exceptions, BaseUserManager, models, schemas
from fastapi_users.models import UP
from sqlalchemy import select


async def sql_get_by_tg_id(self, tg_id: int) -> UP | None:
    statement = select(self.user_table).where(self.user_table.tg_id == tg_id)
    return await self._get_user(statement)


async def manager_get_by_tg_id(self, tg_id: int) -> models.UP:
    """
    Get a user by Telegram ID.

    :param self: BaseUserManager object.
    :param tg_id: Telegram user ID.
    :raises UserNotExists: The user does not exist.
    :return: A user.
    """
    user = await self.user_db.get_by_tg_id(tg_id)

    if user is None:
        raise exceptions.UserNotExists()

    return user


async def authenticate(
        self: BaseUserManager, credentials: OAuth2PasswordRequestForm
) -> models.UP | None:
    """
    Authenticate and return a user following an email and a password.

    Will automatically upgrade password hash if necessary.

    :param self: BaseUserManager object.
    :param credentials: The user credentials.
    """
    try:
        if credentials.username.isdigit():
            user = await self.get_by_tg_id(int(credentials.username))
        else:
            user = await self.get_by_email(credentials.username)
    except exceptions.UserNotExists:
        # Run the hasher to mitigate timing attack
        # Inspired from Django: https://code.djangoproject.com/ticket/20760
        self.password_helper.hash(credentials.password)
        return None

    verified, updated_password_hash = self.password_helper.verify_and_update(
        credentials.password, user.hashed_password
    )
    if not verified:
        return None
    # Update password hash to a more robust one if needed
    if updated_password_hash is not None:
        await self.user_db.update(user, {"hashed_password": updated_password_hash})

    return user


async def create(
        self,
        user_create: schemas.UC,
        safe: bool = False,
        request: Request | None = None,
) -> models.UP:
    """
    Create a user in database.

    Triggers the on_after_register handler on success.

    :param self: BaseUserManager object.
    :param user_create: The UserCreate model to create.
    :param safe: If True, sensitive values like is_superuser or is_verified
    will be ignored during the creation, defaults to False.
    :param request: Optional FastAPI request that
    triggered the operation, defaults to None.
    :raises UserAlreadyExists: A user already exists with the same e-mail.
    :return: A new user.
    """
    await self.validate_password(user_create.password, user_create)

    existing_user = await self.user_db.get_by_email(user_create.email)
    if existing_user is not None:
        raise exceptions.UserAlreadyExists()

    existing_user = await self.user_db.get_by_tg_id(user_create.tg_id)
    if existing_user is not None:
        raise exceptions.UserAlreadyExists()

    user_dict = (
        user_create.create_update_dict()
        if safe
        else user_create.create_update_dict_superuser()
    )
    password = user_dict.pop("password")
    user_dict["hashed_password"] = self.password_helper.hash(password)

    created_user = await self.user_db.create(user_dict)

    await self.on_after_register(created_user, request)

    return created_user
