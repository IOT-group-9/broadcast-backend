from typing import Any, AsyncGenerator

import pytest
from fastapi import FastAPI
from httpx import AsyncClient
from piccolo.conf.apps import Finder
from piccolo.engine.postgres import PostgresEngine
from piccolo.table import create_tables, drop_tables

from app.settings import settings
from app.web.application import get_app


@pytest.fixture(scope="session")
def anyio_backend() -> str:
    """
    Backend for anyio pytest plugin.

    :return: backend name.
    """
    return "asyncio"


async def drop_database(engine: PostgresEngine) -> None:
    """
    Drops test database.

    :param engine: engine connected to postgres database.
    """
    await engine.run_ddl(
        "SELECT pg_terminate_backend(pg_stat_activity.pid) "  # noqa: S608
        "FROM pg_stat_activity "
        f"WHERE pg_stat_activity.datname = '{settings.db_base}' "
        "AND pid <> pg_backend_pid();",
    )
    await engine.run_ddl(
        f"DROP DATABASE {settings.db_base};",
    )


@pytest.fixture(autouse=True)
async def setup_db() -> AsyncGenerator[None, None]:
    """
    Fixture to create all tables before test and drop them after.

    :yield: nothing.
    """
    engine = PostgresEngine(
        config={
            "database": "postgres",
            "user": settings.db_user,
            "password": settings.db_pass,
            "host": settings.db_host,
            "port": settings.db_port,
        },
    )
    await engine.start_connection_pool()

    db_exists = await engine.run_ddl(
        f"SELECT 1 FROM pg_database WHERE datname='{settings.db_base}'",  # noqa: S608
    )
    if db_exists:
        await drop_database(engine)
    await engine.run_ddl(f"CREATE DATABASE {settings.db_base}")
    tables = Finder().get_table_classes()
    create_tables(*tables, if_not_exists=True)

    yield

    drop_tables(*tables)
    await drop_database(engine)


@pytest.fixture
def fastapi_app() -> FastAPI:
    """
    Fixture for creating FastAPI app.

    :return: fastapi app with mocked dependencies.
    """
    application = get_app()
    return application  # noqa: RET504


@pytest.fixture
async def client(
    fastapi_app: FastAPI,
    anyio_backend: Any,
) -> AsyncGenerator[AsyncClient, None]:
    """
    Fixture that creates client for requesting server.

    :param fastapi_app: the application.
    :yield: client for the app.
    """
    async with AsyncClient(app=fastapi_app, base_url="http://test", timeout=2.0) as ac:
        yield ac
