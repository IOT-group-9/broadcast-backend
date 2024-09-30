from piccolo.apps.migrations.auto.migration_manager import MigrationManager
from piccolo.columns.column_types import Integer
from piccolo.columns.column_types import Varchar
from piccolo.columns.indexes import IndexMethod


ID = "2024-09-28T01:22:00:355497"
VERSION = "1.19.0"
DESCRIPTION = ""


async def forwards() -> MigrationManager:
    manager = MigrationManager(
        migration_id=ID, app_name="app_db", description=DESCRIPTION
    )

    manager.add_table(
        class_name="DummyModel",
        tablename="dummy_model",
        schema=None,
        columns=None,
    )

    manager.add_column(
        table_class_name="DummyModel",
        tablename="dummy_model",
        column_name="name",
        db_column_name="name",
        column_class_name="Varchar",
        column_class=Varchar,
        params={
            "length": 200,
            "default": "",
            "null": False,
            "primary_key": False,
            "unique": False,
            "index": False,
            "index_method": IndexMethod.btree,
            "choices": None,
            "db_column_name": None,
            "secret": False,
        },
        schema=None,
    )

    manager.add_column(
        table_class_name="DummyModel",
        tablename="dummy_model",
        column_name="age",
        db_column_name="age",
        column_class_name="Integer",
        column_class=Integer,
        params={
            "default": 0,
            "null": False,
            "primary_key": False,
            "unique": False,
            "index": False,
            "index_method": IndexMethod.btree,
            "choices": None,
            "db_column_name": None,
            "secret": False,
        },
        schema=None,
    )

    return manager
