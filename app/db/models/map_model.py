from piccolo.columns import Integer, Varchar, Serial,ForeignKey, Boolean
from piccolo.table import Table
from app.db.models.parking_place_model import ParkingPlaceModel



class MapModel(Table):
    """Model for carpark."""
    id: Serial  # Add an annotation
    parking_place = ForeignKey(ParkingPlaceModel)
    level = Integer()
    x1 = Integer()
    y1 = Integer()
    x2 = Integer()
    y2 = Integer()
    
class MapSlotModel(Table):
    """Model for carpark."""
    id: Serial  # Add an annotation
    map = ForeignKey(MapModel)
    x1 = Integer()
    y1 = Integer()
    x2 = Integer()
    y2 = Integer()
    ardiuno = Varchar()
    occupied = Boolean()
    avaliable = Boolean()