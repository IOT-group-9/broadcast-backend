from piccolo.columns import ForeignKey, Integer, Serial
from piccolo.table import Table

from .parking_place_model import ParkingPlaceModel


class DisplayModel(Table):
    """Model for display."""

    id: Serial  # Add an annotation
    parking_place = ForeignKey(ParkingPlaceModel)
    level = Integer()
