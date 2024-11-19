import logging
from fastapi import APIRouter, HTTPException
from piccolo_api.crud.endpoints import PiccoloCRUD
from piccolo_api.fastapi.endpoints import FastAPIWrapper

from app.db.models.models import Arduino, MapSlot

logging.basicConfig(level=logging.INFO)
sensor_router = APIRouter()


# CRUD endpoints for Arduino
FastAPIWrapper(
    root_url="/arduino",
    fastapi_app=sensor_router,
    piccolo_crud=PiccoloCRUD(
        table=Arduino,
        read_only=False,
    ),
)

# CRUD endpoints for Arduino
FastAPIWrapper(
    root_url="/mapslot",
    fastapi_app=sensor_router,
    piccolo_crud=PiccoloCRUD(
        table=MapSlot,
        read_only=False,
    ),
)