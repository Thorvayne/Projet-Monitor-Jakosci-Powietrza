from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker, declarative_base


DATABASE_URL = "sqlite+aiosqlite:///./baza_lokalna.db"


engine = create_async_engine(
    DATABASE_URL, 
    connect_args={"check_same_thread": False}, 
    echo=True
)

SessionLocal = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

Base = declarative_base()

async def get_db():
    async with SessionLocal() as session:
        yield session