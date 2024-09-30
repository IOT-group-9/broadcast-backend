from piccolo.columns import Integer, Varchar
from piccolo.table import Table


class DummyModel(Table):
    """Model for demo purpose."""

    name = Varchar(length=200)
    age = Integer()
