from fastapi import HTTPException, Request, WebSocket
from taskiq import TaskiqDepends


async def get_pubsub(request: Request = None, websocket: WebSocket = None):
    if request:
        return request.app.state.pubsub
    elif websocket:
        return websocket.app.state.pubsub
    else:
        raise HTTPException(status_code=400, detail="No Request or WebSocket provided")
