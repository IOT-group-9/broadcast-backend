from fastapi import APIRouter, Depends, WebSocket
from fastapi_websocket_pubsub import PubSubEndpoint
from loguru import logger

from app.db.models.models import Map, MapSlot
from app.services.pubsub.dependency import get_pubsub

router = APIRouter()


@router.websocket("/subscribe")
async def websocket_rpc_endpoint(
    websocket: WebSocket,
    pubsub: PubSubEndpoint = Depends(get_pubsub),
) -> None:
    """Init websocket and subscription for app."""
    await pubsub.main_loop(websocket)
    try:
        # Close connection if not already closed
        await websocket.close()
    except Exception as e:
        logger.info(e)


@router.get("/publish/{parking_place_id}/{level}")
async def publish_parking(
    parking_place_id: int,
    level: int,
    pubsub: PubSubEndpoint = Depends(get_pubsub),
) -> dict:
    """Send updated details to subscribed apps."""
    map = await Map.select().where(Map.parking_place == parking_place_id, Map.level_no == level).first()
    map_slots = await MapSlot.select().where(MapSlot.map == map.get('id'))
    await pubsub.publish(
        topics=[f"{parking_place_id}/{level}"],
        data={"map": map, "map_slots": map_slots},
    )
    return {}
