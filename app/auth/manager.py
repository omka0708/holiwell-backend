from typing import Optional

from fastapi import Depends, Request, Response
from fastapi_users import BaseUserManager, IntegerIDMixin

from app.auth.email import forgot_password_mail
from app.auth.models import User
from app.auth.schemas import EmailSchema
from app.utils import get_user_db
from app.config import SECRET_AUTH


class UserManager(IntegerIDMixin, BaseUserManager[User, int]):
    reset_password_token_secret = SECRET_AUTH
    verification_token_secret = SECRET_AUTH

    async def on_after_login(self, user: User, request: Optional[Request] = None, response: Optional[Response] = None):
        print(f"User {user.id} has logged in.")

    async def on_after_register(self, user: User, request: Optional[Request] = None):
        print(f"User {user.id} has registered.")

    async def on_after_forgot_password(
            self, user: User, token: str, request: Optional[Request] = None
    ):
        payload = await request.json()
        email = EmailSchema(email=[payload['email'], ])
        print(f"User {user.id} has forgot their password. Reset token: {token}")
        await forgot_password_mail(email=email, token=token)

    async def on_after_request_verify(
            self, user: User, token: str, request: Optional[Request] = None
    ):
        print(f"Verification requested for user {user.id}. Verification token: {token}")


async def get_user_manager(user_db=Depends(get_user_db)):
    yield UserManager(user_db)
