from fastapi_users import FastAPIUsers
from fastapi_users.authentication import CookieTransport, JWTStrategy, AuthenticationBackend

from app.config import SECRET_AUTH

from app.auth.manager import get_user_manager
from app.auth.models import User

cookie_transport = CookieTransport(
    cookie_name='holiwell_jwt_cookie',
    cookie_samesite='none',
    cookie_httponly=False,
    cookie_secure=False
)

SECRET = SECRET_AUTH


def get_jwt_strategy() -> JWTStrategy:
    return JWTStrategy(secret=SECRET, lifetime_seconds=None)


auth_backend = AuthenticationBackend(
    name="jwt",
    transport=cookie_transport,
    get_strategy=get_jwt_strategy,
)

fastapi_users = FastAPIUsers[User, int](
    get_user_manager,
    [auth_backend],
)
