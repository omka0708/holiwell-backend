from fastapi_users import FastAPIUsers, BaseUserManager
from fastapi_users.authentication import BearerTransport, JWTStrategy, AuthenticationBackend
from fastapi_users_db_sqlalchemy import SQLAlchemyUserDatabase

from app.auth.manager import get_user_manager
from app.auth.models import User
from app.config import SECRET_AUTH

from .override import sql_get_by_tg_id, manager_get_by_tg_id, authenticate, create

bearer_transport = BearerTransport(tokenUrl="auth/jwt/login")

SECRET = SECRET_AUTH


def get_jwt_strategy() -> JWTStrategy:
    return JWTStrategy(secret=SECRET, lifetime_seconds=None)


SQLAlchemyUserDatabase.get_by_tg_id = sql_get_by_tg_id
BaseUserManager.get_by_tg_id = manager_get_by_tg_id
BaseUserManager.authenticate = authenticate
BaseUserManager.create = create

auth_backend = AuthenticationBackend(
    name="jwt",
    transport=bearer_transport,
    get_strategy=get_jwt_strategy,
)

fastapi_users = FastAPIUsers[User, int](
    get_user_manager,
    [auth_backend],
)
