from __future__ import annotations

import datetime
from uuid import uuid4


def default_guid() -> str:
    return str(uuid4())


def fake_guid() -> str:
    return "abc-123"


def default_datetime() -> datetime.datetime:
    return datetime.datetime.now(datetime.UTC)


def fake_datetime() -> datetime.datetime:
    return datetime.datetime(2025, 1, 1, 12, tzinfo=datetime.UTC)
