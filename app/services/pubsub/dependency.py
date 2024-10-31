from fastapi import HTTPException, Request, WebSocket
from fastapi_websocket_pubsub import PubSubEndpoint


async def get_pubsub(
    request: Request = None,
    websocket: WebSocket = None,
) -> PubSubEndpoint:
    """Change based on websocket or http."""
    if request:
        return request.app.state.pubsub
    if websocket:
        return websocket.app.state.pubsub
    raise HTTPException(status_code=400, detail="No Request or WebSocket provided")
