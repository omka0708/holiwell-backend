from dotenv import load_dotenv
import os

load_dotenv()

DB_USER = os.environ.get("DB_USER")
DB_PASS = os.environ.get("DB_PASS")
DB_HOST = os.environ.get("DB_HOST")
DB_PORT = os.environ.get("DB_PORT")
DB_NAME = os.environ.get("DB_NAME")

SECRET_AUTH = os.environ.get("SECRET_AUTH")

MAIL_USERNAME = os.environ.get("MAIL_USERNAME")
MAIL_PASSWORD = os.environ.get("MAIL_PASSWORD")
MAIL_FROM = os.environ.get("MAIL_FROM")
MAIL_PORT = os.environ.get("MAIL_PORT")
MAIL_SERVER = os.environ.get("MAIL_SERVER")
MAIL_FROM_NAME = os.environ.get("MAIL_FROM_NAME")
MAIL_STARTTLS = os.environ.get("MAIL_STARTTLS")
MAIL_SSL_TLS = os.environ.get("MAIL_SSL_TLS")
USE_CREDENTIALS = os.environ.get("USE_CREDENTIALS")
VALIDATE_CERTS = os.environ.get("VALIDATE_CERTS")

SERVER_URL = os.environ.get("SERVER_URL")
