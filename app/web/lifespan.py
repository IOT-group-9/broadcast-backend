from contextlib import asynccontextmanager
from typing import AsyncGenerator

from fastapi import FastAPI

from app.services.pubsub.lifespan import init_pubsub
from app.services.rabbit.lifespan import init_rabbit, shutdown_rabbit
from app.services.redis.lifespan import init_redis, shutdown_redis
from app.settings import settings
from app.tkq import broker


@asynccontextmanager
async def lifespan_setup(
    app: FastAPI,
) -> AsyncGenerator[None, None]:  # pragma: no cover
    """
    Actions to run on application startup.

    This function uses fastAPI app to store data
    in the state, such as db_engine.

    :param app: the fastAPI application.
    :return: function that actually performs actions.
    """

    app.middleware_stack = None
    if settings.enable_taskiq:
        if not broker.is_worker_process:
            await broker.startup()
        init_redis(app)
        init_rabbit(app)
    init_pubsub(app)
    app.middleware_stack = app.build_middleware_stack()

    yield
    if settings.enable_taskiq:
        if not broker.is_worker_process:
            await broker.shutdown()
        await shutdown_redis(app)
        await shutdown_rabbit(app)
