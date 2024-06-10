from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.core.config import Config

engine = create_engine(Config.DATABASE_URL)
session_maker = sessionmaker(
    autocommit=False, autoflush=False, expire_on_commit=False, bind=engine
)
