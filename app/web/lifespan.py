from contextlib import asynccontextmanager
from typing import AsyncGenerator

from fastapi import FastAPI

from app.services.rabbit.lifespan import init_rabbit, shutdown_rabbit
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
    if not broker.is_worker_process:
        await broker.startup()
    init_rabbit(app)
    app.middleware_stack = app.build_middleware_stack()

    yield
    if not broker.is_worker_process:
        await broker.shutdown()
    await shutdown_rabbit(app)
