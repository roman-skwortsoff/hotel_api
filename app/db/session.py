from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import declarative_base
from app.db.base import Base, BASE_DIR, env

# Конфигурация для SQLite
DATABASE_URL = env("DATABASE_URL")
TEST_DATABASE_URL = "sqlite+aiosqlite:///:memory:"

# Создаем движки
async_engine = create_async_engine(
    DATABASE_URL,
    echo=True,
    connect_args={"check_same_thread": False},
    future=True
)

test_async_engine = create_async_engine(
    TEST_DATABASE_URL,
    echo=False,
    connect_args={"check_same_thread": False},
    future=True
)

# Фабрики сессий
AsyncSessionLocal = async_sessionmaker(
    bind=async_engine,
    class_=AsyncSession,
    expire_on_commit=False
)

async def init_db():
    """Инициализация таблиц (аналог create_all)"""
    async with async_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

async def get_async_db() -> AsyncSession:
    """Генератор сессий для зависимостей FastAPI"""
    async with AsyncSessionLocal() as db:
        try:
            yield db
        finally:
            await db.close()


# синхронная база для ранее созданных шаблонов для записи

from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine

sync_engine = create_engine(env("SYNC_DATABASE_URL"))
SessionLocal = sessionmaker(bind=sync_engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# DATABASE_URL = "sqlite:///./test.db"  # Для разработки
# engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
# SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
# def get_db():
#     db = SessionLocal()
#     try:
#         yield db
#     finally:
#         db.close()

# ниже для синхронного кода

# from sqlalchemy import create_engine
# from sqlalchemy.orm import sessionmaker
#
# DATABASE_URL = "sqlite:///./test.db"  # Для разработки
# engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
# SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
#
# # Тестовая БД (отдельный файл)
# TEST_DATABASE_URL = "sqlite:///./test_base.db"
# test_engine = create_engine(TEST_DATABASE_URL, connect_args={"check_same_thread": False})
# TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=test_engine)
#
# def get_db():
#     db = SessionLocal()
#     try:
#         yield db
#     finally:
#         db.close()
#
# def get_db_test():
#     db = TestingSessionLocal()
#     try:
#         yield db
#     finally:
#         db.close()