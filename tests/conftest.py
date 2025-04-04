import pytest
from httpx import AsyncClient
from app.main import app
from app.db.base import Base
from app.db.session import test_async_engine, get_async_db
from sqlalchemy.ext.asyncio import async_sessionmaker, AsyncSession


@pytest.fixture(scope="function", autouse=True)
async def setup_db():
    """Фикстура для создания/удаления таблиц перед каждым тестом"""
    async with test_async_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    async with test_async_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


@pytest.fixture
async def db_session():
    """Фикстура тестовой сессии с изолированной транзакцией"""
    async with test_async_engine.connect() as conn:
        # Начинаем новую транзакцию
        await conn.begin()

        # Настраиваем сессию
        TestingSessionLocal = async_sessionmaker(
            bind=conn,
            class_=AsyncSession,
            expire_on_commit=False,
            autoflush=False
        )

        async with TestingSessionLocal() as session:
            try:
                yield session
            finally:
                # Откатываем транзакцию после теста
                await session.rollback()
                await session.close()

        # Закрываем соединение
        await conn.close()


@pytest.fixture
async def async_client(db_session):
    """Фикстура тестового клиента с подменой зависимостей"""
    # Подменяем зависимость get_async_db
    original_dependency = app.dependency_overrides.get(get_async_db)
    app.dependency_overrides[get_async_db] = lambda: db_session

    async with AsyncClient(
            app=app,
            base_url="http://test",
            follow_redirects=True
    ) as client:
        yield client

    # Восстанавливаем оригинальную зависимость
    if original_dependency is not None:
        app.dependency_overrides[get_async_db] = original_dependency
    else:
        app.dependency_overrides.pop(get_async_db, None)

# @pytest.fixture(scope="module")
# def test_db():
#     # Создаем таблицы перед тестами
#     Base.metadata.create_all(bind=test_engine)
#     yield
#     # Очищаем после тестов
#     Base.metadata.drop_all(bind=test_engine)
#
#
# @pytest.fixture
# def db_session(test_db):
#     # Новая сессия для каждого теста
#     connection = test_engine.connect()
#     transaction = connection.begin()
#     session = TestingSessionLocal(bind=connection)
#
#     yield session
#
#     # Откатываем изменения после теста
#     session.close()
#     transaction.rollback()
#     connection.close()
#
#
# @pytest.fixture
# def client(db_session):
#     # Переопределяем зависимость get_db
#     def override_get_db():
#         try:
#             yield db_session
#         finally:
#             db_session.close()
#
#     app.dependency_overrides[get_db] = override_get_db
#     with TestClient(app) as test_client:
#         yield test_client