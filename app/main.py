from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import RedirectResponse, Response

from app.auth.auth import auth_backend, fastapi_users
from app.auth.schemas import UserRead, UserCreate
from .routers import user, trainer, lesson, course

app = FastAPI(title='Holiwell API')


@app.get("/", include_in_schema=False)
async def redirect_to_docs():
    return RedirectResponse(url='/docs')


@app.options("/{path:path}", include_in_schema=False)
async def preflight_handler():
    return Response(status_code=200)


app.include_router(
    fastapi_users.get_auth_router(auth_backend),
    prefix="/auth/jwt",
    tags=["auth"],
)

app.include_router(
    fastapi_users.get_register_router(UserRead, UserCreate),
    prefix="/auth",
    tags=["auth"],
)

app.include_router(
    fastapi_users.get_reset_password_router(),
    prefix="/auth",
    tags=["auth"],
)


@app.get("/change-password", include_in_schema=False)
async def change_password(token: str):
    return {
        'token': token
    }


app.include_router(
    user.router,
    prefix="/api/users",
    tags=["user"],
)

app.include_router(
    trainer.router,
    prefix="/api/trainers",
    tags=["trainer"],
)

app.include_router(
    lesson.router,
    prefix="/api/lessons",
    tags=["lesson"],
)

app.include_router(
    course.router,
    prefix="/api/courses",
    tags=["course"],
)

origins = [
    "http://localhost",
    "http://localhost:8000",
    "http://localhost:3000",
    "http://154.194.52.246",
    "http://154.194.52.246:8000"
    "http://154.194.52.246:3000",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "OPTIONS", "DELETE", "PATCH", "PUT"],
    expose_headers=["Content-Type", "Content-Length", "Access-Control-Allow-Headers", "Access-Control-Allow-Origin",
                    "Authorization", "Accept", "Accept-Encoding", "Accept-Language", "Content-Language", "Range",
                    "X-Requested-With", "Cookie", "Set-Cookie", "Connection", "Host", "Origin", "Referer", "User-Agent",
                    "Access-Control-Expose-Headers"],
    allow_headers=["Content-Type", "Content-Length", "Access-Control-Allow-Headers", "Access-Control-Allow-Origin",
                   "Authorization", "Accept", "Accept-Encoding", "Accept-Language", "Content-Language", "Range",
                   "X-Requested-With", "Cookie", "Set-Cookie", "Connection", "Host", "Origin", "Referer", "User-Agent",
                   "Access-Control-Expose-Headers"],
)
