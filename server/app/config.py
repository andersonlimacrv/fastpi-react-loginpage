from typing import Any
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
from sqlmodel import SQLModel
import os
from dotenv import load_dotenv

load_dotenv() 

DATABASE_URL = os.getenv('DATABASE_URL')
SECRET_KEY = os.getenv('SECRET_KEY')
ALGORITHM = os.getenv('ALGORITHM')
ACESS_TOKEN_EXPIRE = int(os.getenv('ACESS_TOKEN_EXPIRE'))

class AsynsDatabaseSession:
    def __init__(self) -> None:
        self.session = None
        self.engine = None

    def __getattr__(self,name):
        return getattr(self.session, name)
    
    def init(self):
        self.engine = create_async_engine(DATABASE_URL, future=True, echo=True)
        self.session = sessionmaker(self.engine, expire_on_commit=False ,class_=AsyncSession)

    async def create_all(self):
        async with self.engine.begin() as conn:
            await conn.run_sync(SQLModel.metadata.create_all)

db = AsynsDatabaseSession()

async def commit_rollback():
    try:
        await db.commit()
    except Exception:
        await db.rollback()
        raise
