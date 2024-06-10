import os

from dotenv import load_dotenv

load_dotenv()

POSTGRES_USER = os.environ.get("POSTGRES_USER")
POSTGRES_PASSWORD = os.environ.get("POSTGRES_PASSWORD")
POSTGRES_DB = os.environ.get("POSTGRES_DB")
POSTGRES_HOST = os.environ.get("POSTGRES_HOST")
POSTGRES_PORT = os.environ.get("POSTGRES_PORT")


class Config:
    SECRET_KEY = os.environ.get("SECRET_KEY")

    DATABASE_URL = f"postgresql://{POSTGRES_USER}:{POSTGRES_PASSWORD}@{POSTGRES_HOST}:{POSTGRES_PORT}/{POSTGRES_DB}"

    USER_SESSION_EXPIRY = int(os.environ.get("USER_SESSION_EXPIRY"))
    USER_SESSION_REFRESH = int(os.environ.get("USER_SESSION_REFRESH"))
    SALT_SIZE = int(os.environ.get("SALT_SIZE"))
