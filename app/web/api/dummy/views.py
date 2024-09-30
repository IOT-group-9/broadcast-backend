from fastapi import APIRouter
from piccolo_api.crud.endpoints import PiccoloCRUD
from piccolo_api.fastapi.endpoints import FastAPIWrapper

from app.db.models.dummy_model import DummyModel

router = APIRouter()
FastAPIWrapper(
    root_url="/",
    fastapi_app=router,
    piccolo_crud=PiccoloCRUD(
        table=DummyModel,
        read_only=False,
    ),
)
