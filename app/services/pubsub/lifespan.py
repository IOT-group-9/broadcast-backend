from fastapi import FastAPI
from fastapi_websocket_pubsub import PubSubEndpoint
from app.settings import settings

def init_pubsub(app: FastAPI) -> None:  # pragma: no cover
    app.state.pubsub = PubSubEndpoint(broadcaster = settings.db_url.__str__())
    
    
    