from fastapi.routing import APIRouter, Mount
from piccolo.apps.user.tables import BaseUser
from piccolo.conf.apps import table_finder
from piccolo_admin.endpoints import create_admin

from app.web.api import docs, dummy, echo, monitoring

api_router = APIRouter()
api_router.include_router(monitoring.router)
api_router.include_router(docs.router)
api_router.include_router(echo.router, prefix="/echo", tags=["echo"])
api_router.include_router(dummy.router, prefix="/dummy", tags=["dummy"])
admin_route = Mount(
    path="/admin/",
    app=create_admin(
        tables=[*table_finder(modules=["app.db.models.dummy_model"]), BaseUser],
        # Specify a different site name in the
        # admin UI (default Piccolo Admin):
        site_name="My Site Admin",
        # Required when running under HTTPS:
        # ERA001 allowed_hosts=["my_site.com"],
    ),
)
