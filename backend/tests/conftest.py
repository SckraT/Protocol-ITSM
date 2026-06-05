"""
Фикстуры для тестов.
Используется in-memory SQLite с async SQLAlchemy.

Клиенты:
  - anon_client   — без авторизации (для тестов /auth)
  - client        — авторизован как admin (дефолт для большинства тестов CRUD)
  - editor_client — роль editor
  - viewer_client — роль viewer

Хелперы сидирования (импортируются в тестах):
  - _seed_user, _seed_department, _seed_executor, _seed_meeting, _seed_item
"""
import pytest_asyncio
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from app.database import get_db
from app.main import app
from app.models import Base
from app.models.department import Department
from app.models.executor import Executor
from app.models.item import Item
from app.models.meeting import Meeting
from app.models.user import RoleEnum, User
from app.security import create_access_token, hash_password

# URL для тестовой in-memory БД
TEST_DATABASE_URL = "sqlite+aiosqlite:///:memory:"

# Пароль сидируемых тестовых пользователей (≥8 символов)
TEST_PASSWORD = "password123"


@pytest_asyncio.fixture(autouse=True)
def _reset_rate_limit():
    """Сбрасывать состояние rate-limiter перед каждым тестом (изоляция)."""
    from app.middleware.rate_limit import reset_rate_limit

    reset_rate_limit()
    yield


@pytest_asyncio.fixture(scope="function")
async def async_engine():
    """Создаёт async engine с in-memory SQLite для каждого теста."""
    engine = create_async_engine(TEST_DATABASE_URL, echo=False)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield engine
    await engine.dispose()


@pytest_asyncio.fixture(scope="function")
async def db_session(async_engine):
    """Предоставляет сессию к тестовой БД."""
    session_factory = async_sessionmaker(
        async_engine,
        class_=AsyncSession,
        expire_on_commit=False,
    )
    async with session_factory() as session:
        yield session


async def _seed_user(
    session: AsyncSession,
    username: str,
    role: RoleEnum,
    *,
    email: str | None = None,
    phone: str | None = None,
    must_change_password: bool = False,
    last_name: str | None = None,
    first_name: str | None = None,
    middle_name: str | None = None,
) -> User:
    """Создать пользователя в тестовой БД и вернуть его."""
    user = User(
        username=username,
        hashed_password=hash_password(TEST_PASSWORD),
        role=role,
        is_active=True,
        must_change_password=must_change_password,
        email=email,
        phone=phone,
        last_name=last_name,
        first_name=first_name,
        middle_name=middle_name,
    )
    session.add(user)
    await session.flush()
    return user


async def _seed_department(
    session: AsyncSession,
    name: str = "Тестовый отдел",
) -> Department:
    """Создать отдел в тестовой БД."""
    dept = Department(name=name)
    session.add(dept)
    await session.flush()
    return dept


async def _seed_executor(
    session: AsyncSession,
    name: str = "Тестовый исполнитель",
    *,
    department_id: int | None = None,
    user_id: int | None = None,
) -> Executor:
    """Создать исполнителя в тестовой БД (опционально в отделе / с привязкой к УЗ)."""
    executor = Executor(
        name=name,
        department_id=department_id,
        user_id=user_id,
    )
    session.add(executor)
    await session.flush()
    return executor


async def _seed_meeting(
    session: AsyncSession,
    title: str = "Тестовое совещание",
    *,
    meeting_date=None,
    description: str | None = None,
    participant_ids: list[int] | None = None,
) -> Meeting:
    """Создать совещание в тестовой БД."""
    from datetime import date

    meeting = Meeting(
        title=title,
        meeting_date=meeting_date or date(2026, 6, 5),
        description=description,
    )
    session.add(meeting)
    await session.flush()

    if participant_ids:
        from sqlalchemy import select

        from app.models.executor import Executor as ExecutorModel

        result = await session.execute(
            select(ExecutorModel).where(ExecutorModel.id.in_(participant_ids))
        )
        meeting.participants = list(result.scalars().all())
        await session.flush()

    return meeting


async def _seed_item(
    session: AsyncSession,
    topic: str = "Тестовая задача",
    *,
    ticket: str | None = None,
    priority: str | None = None,
    state: str = "in_progress",
    due_date=None,
    meeting_id: int | None = None,
    executor_ids: list[int] | None = None,
    status_note: str | None = None,
    status_date=None,
) -> Item:
    """Создать задачу (опционально с испололнителями, совещанием и начальным статусом)."""
    from datetime import date

    from app.models.status import Status

    item = Item(
        topic=topic,
        ticket=ticket,
        priority=priority,
        state=state,
        due_date=due_date,
        meeting_id=meeting_id,
    )
    session.add(item)
    await session.flush()

    if executor_ids:
        from sqlalchemy import select

        from app.models.executor import Executor as ExecutorModel

        result = await session.execute(
            select(ExecutorModel).where(ExecutorModel.id.in_(executor_ids))
        )
        item.executors = list(result.scalars().all())
        await session.flush()

    if status_note is not None or status_date is not None:
        status = Status(
            item_id=item.id,
            status_note=status_note,
            status_date=status_date or date(2026, 6, 5),
        )
        session.add(status)
        await session.flush()

    return item


def _make_client(db_session: AsyncSession, token: str | None) -> AsyncClient:
    """Собрать AsyncClient с переопределением БД и опциональным Bearer-токеном."""

    async def override_get_db():
        yield db_session

    app.dependency_overrides[get_db] = override_get_db
    headers = {"Authorization": f"Bearer {token}"} if token else {}
    return AsyncClient(transport=ASGITransport(app=app), base_url="http://test", headers=headers)


@pytest_asyncio.fixture(scope="function")
async def anon_client(db_session):
    """Неавторизованный клиент (для /auth-тестов)."""
    async with _make_client(db_session, None) as c:
        yield c
    app.dependency_overrides.clear()


@pytest_asyncio.fixture(scope="function")
async def client(db_session):
    """Авторизован как admin — дефолт для CRUD-тестов."""
    await _seed_user(db_session, "admin_t", RoleEnum.admin)
    token = create_access_token("admin_t", RoleEnum.admin.value)
    async with _make_client(db_session, token) as c:
        yield c
    app.dependency_overrides.clear()


@pytest_asyncio.fixture(scope="function")
async def editor_client(db_session):
    """Авторизован как editor."""
    await _seed_user(db_session, "editor_t", RoleEnum.editor)
    token = create_access_token("editor_t", RoleEnum.editor.value)
    async with _make_client(db_session, token) as c:
        yield c
    app.dependency_overrides.clear()


@pytest_asyncio.fixture(scope="function")
async def viewer_client(db_session):
    """Авторизован как viewer."""
    await _seed_user(db_session, "viewer_t", RoleEnum.viewer)
    token = create_access_token("viewer_t", RoleEnum.viewer.value)
    async with _make_client(db_session, token) as c:
        yield c
    app.dependency_overrides.clear()
