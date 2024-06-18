from fastapi_mail import ConnectionConfig, MessageSchema, MessageType, FastMail

from app.auth.schemas import EmailSchema
from app.config import (MAIL_USERNAME, MAIL_PASSWORD, MAIL_FROM, MAIL_PORT, MAIL_SERVER, MAIL_FROM_NAME,
                        MAIL_STARTTLS, MAIL_SSL_TLS, USE_CREDENTIALS, VALIDATE_CERTS, SERVER_URL)

conf = ConnectionConfig(
    MAIL_USERNAME=MAIL_USERNAME,
    MAIL_PASSWORD=MAIL_PASSWORD,
    MAIL_FROM=MAIL_FROM,
    MAIL_PORT=MAIL_PORT,
    MAIL_SERVER=MAIL_SERVER,
    MAIL_FROM_NAME=MAIL_FROM_NAME,
    MAIL_STARTTLS=MAIL_STARTTLS,
    MAIL_SSL_TLS=MAIL_SSL_TLS,
    USE_CREDENTIALS=USE_CREDENTIALS,
    VALIDATE_CERTS=VALIDATE_CERTS
)


async def forgot_password_mail(email: EmailSchema, token: str):
    html = f"""<p>{SERVER_URL}change-password?token={token}</p>"""

    message = MessageSchema(
        subject="Восстановление забытого пароля",
        recipients=email.dict().get("email"),
        body=html,
        subtype=MessageType.html)

    fm = FastMail(conf)
    await fm.send_message(message)
