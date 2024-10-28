import asyncio
from fastapi import APIRouter, Depends, HTTPException, WebSocket, status
from app import settings
from app.db.models.map_model import MapModel, MapSlotModel
from app.db.models.parking_place_model import ParkingPlaceModel
from app.db.models.display_model import DisplayModel
from app.services.pubsub.dependency import get_pubsub
from fastapi_websocket_pubsub import PubSubEndpoint
from fastapi_websocket_pubsub import PubSubClient

router = APIRouter()

@router.websocket("/subscribe")
async def websocket_rpc_endpoint(websocket: WebSocket, pubsub: PubSubEndpoint = Depends(get_pubsub)):
    maps = await MapModel.select()
    maps_slots = await MapSlotModel.select()
    await pubsub.main_loop(websocket)
    try:
        # Close connection if not already closed
        await websocket.close()
    except:
        pass

@router.get("/publish/{parking_place_id}/{level}")
async def publish_parking(parking_place_id: int, level: int, pubsub: PubSubEndpoint = Depends(get_pubsub)):
    map = await MapModel.select().where(MapModel.parking_place.id == parking_place_id, MapModel.level == level).first()
    map_slots = await MapSlotModel.select().where(MapSlotModel.map == map)
    await pubsub.publish(topics = [f"{parking_place_id}/{level}"], data = {"map": map, "map_slots": map_slots})
    return {}

