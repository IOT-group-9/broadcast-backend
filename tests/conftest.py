import uuid
from typing import Any, AsyncGenerator
from unittest.mock import Mock

import pytest
from aio_pika import Channel
from aio_pika.abc import AbstractExchange, AbstractQueue
from aio_pika.pool import Pool
from fakeredis import FakeServer
from fakeredis.aioredis import FakeConnection
from fastapi import FastAPI
from httpx import AsyncClient
from piccolo.conf.apps import Finder
from piccolo.engine.postgres import PostgresEngine
from piccolo.table import create_tables, drop_tables
from redis import VERSION
from redis.asyncio import ConnectionPool

from app.services.rabbit.dependencies import get_rmq_channel_pool
from app.services.rabbit.lifespan import init_rabbit, shutdown_rabbit
from app.services.redis.dependency import get_redis_pool
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
async def test_rmq_pool() -> AsyncGenerator[Channel, None]:
    """
    Create rabbitMQ pool.

    :yield: channel pool.
    """
    app_mock = Mock()
    init_rabbit(app_mock)
    yield app_mock.state.rmq_channel_pool
    await shutdown_rabbit(app_mock)


@pytest.fixture
async def test_exchange_name() -> str:
    """
    Name of an exchange to use in tests.

    :return: name of an exchange.
    """
    return uuid.uuid4().hex


@pytest.fixture
async def test_routing_key() -> str:
    """
    Name of routing key to use while binding test queue.

    :return: key string.
    """
    return uuid.uuid4().hex


@pytest.fixture
async def test_exchange(
    test_exchange_name: str,
    test_rmq_pool: Pool[Channel],
) -> AsyncGenerator[AbstractExchange, None]:
    """
    Creates test exchange.

    :param test_exchange_name: name of an exchange to create.
    :param test_rmq_pool: channel pool for rabbitmq.
    :yield: created exchange.
    """
    async with test_rmq_pool.acquire() as conn:
        exchange = await conn.declare_exchange(
            name=test_exchange_name,
            auto_delete=True,
        )
        yield exchange

        await exchange.delete(if_unused=False)


@pytest.fixture
async def test_queue(
    test_exchange: AbstractExchange,
    test_rmq_pool: Pool[Channel],
    test_routing_key: str,
) -> AsyncGenerator[AbstractQueue, None]:
    """
    Creates queue connected to exchange.

    :param test_exchange: exchange to bind queue to.
    :param test_rmq_pool: channel pool for rabbitmq.
    :param test_routing_key: routing key to use while binding.
    :yield: queue binded to test exchange.
    """
    async with test_rmq_pool.acquire() as conn:
        queue = await conn.declare_queue(name=uuid.uuid4().hex)
        await queue.bind(
            exchange=test_exchange,
            routing_key=test_routing_key,
        )
        yield queue

        await queue.delete(if_unused=False, if_empty=False)


@pytest.fixture
async def fake_redis_pool() -> AsyncGenerator[ConnectionPool, None]:
    """
    Get instance of a fake redis.

    :yield: FakeRedis instance.
    """
    server = FakeServer(version=VERSION, server_type="redis")
    server.connected = True
    pool = ConnectionPool(
        connection_class=FakeConnection,
        server=server,
        version=VERSION,
        server_type="redis",
    )

    yield pool

    await pool.disconnect()


@pytest.fixture
def fastapi_app(
    fake_redis_pool: ConnectionPool,
    test_rmq_pool: Pool[Channel],
) -> FastAPI:
    """
    Fixture for creating FastAPI app.

    :return: fastapi app with mocked dependencies.
    """
    application = get_app()
    application.dependency_overrides[get_redis_pool] = lambda: fake_redis_pool
    application.dependency_overrides[get_rmq_channel_pool] = lambda: test_rmq_pool
    return application


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
