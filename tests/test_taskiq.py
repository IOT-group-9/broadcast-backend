import pytest

from app.tkq import broker


@broker.task
async def parse_int(val: str) -> int:
    """Test stuff."""
    return int(val)


@pytest.mark.anyio
async def test_task() -> None:
    """Test stuff."""
    assert await parse_int("11") == 11
