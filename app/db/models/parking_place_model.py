from piccolo.columns import Integer, Serial, Varchar
from piccolo.table import Table


class ParkingPlaceModel(Table):
    """Model for carpark."""

    id: Serial  # Add an annotation
    location = Varchar()
    levels = Integer()
