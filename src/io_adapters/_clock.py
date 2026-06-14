from __future__ import annotations

import datetime
from abc import ABC, abstractmethod
from uuid import uuid4

import attrs


@attrs.frozen
class BaseClock(ABC):
    @abstractmethod
    def now(self) -> datetime.datetime: ...


@attrs.frozen
class RealClock(BaseClock):
    def now(self) -> datetime.datetime:
        return datetime.datetime.now(datetime.UTC)


@attrs.frozen
class FakeClock(BaseClock):
    datetimes: list[datetime.datetime] = attrs.field(factory=list)

    def now(self) -> datetime.datetime:
        return self.datetimes.pop(0)


def default_guid() -> str:
    return str(uuid4())


def fake_guid() -> str:
    return "abc-123"
