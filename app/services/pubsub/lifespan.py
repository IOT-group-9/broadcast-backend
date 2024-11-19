from fastapi import FastAPI
from fastapi_websocket_pubsub import PubSubEndpoint

from app.settings import settings


def init_pubsub(app: FastAPI) -> None:  # pragma: no cover
    # init pubsub endpoint
    app.state.pubsub = PubSubEndpoint()
    if settings.enable_sqlite == True:
        app.state.pubsub = PubSubEndpoint()
    else:
        app.state.pubsub = PubSubEndpoint(broadcaster=settings.db_url.__str__())
