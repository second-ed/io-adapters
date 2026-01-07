from __future__ import annotations

import logging
from collections.abc import Callable, Hashable
from pathlib import Path
from typing import Concatenate, ParamSpec, TypeAlias

logger = logging.getLogger(__name__)

Data: TypeAlias = "Data"
P = ParamSpec("P")

ReadFn = Callable[Concatenate[str | Path, P], Data]
WriteFn = Callable[Concatenate[Data, str | Path, P], None]


READ_FNS: dict[Hashable, ReadFn] = {}
WRITE_FNS: dict[Hashable, WriteFn] = {}


def register_read_fn(key: Hashable) -> Callable:
    """Register a read function to the read functions constant.

    This is useful for smaller projects where domain isolation isn't required.

    .. code-block:: python

        from io_adapters import RealAdapter, register_read_fn

        @register_read_fn("json")
        def read_json(path: str | Path, **kwargs: dict) -> dict:
            ...

    This function will be accessible when you initialise a ``RealAdapter``
     and a stub of the functionality will be added to a ``FakeAdapter``.
    """
    key = standardise_key(key)

    def wrapper(func: Callable) -> Callable:
        logger.info(f"registering read fn {key = } {func = }")
        READ_FNS[key] = func
        return func

    return wrapper


def register_write_fn(key: Hashable) -> Callable:
    """Register a write function to the write functions constant.

    This is useful for smaller projects where domain isolation isn't required.

    .. code-block:: python

        from enum import Enum
        from io_adapters import RealAdapter, register_write_fn

        class WriteFormat(Enum):
            JSON = "json"

        @register_write_fn(WriteFormat.JSON)
        def write_json(data: dict, path: str | Path, **kwargs: dict) -> None:
            ...

    This function will be accessible when you initialise a ``RealAdapter``
     and a stub of the functionality will be added to a ``FakeAdapter``.
    """
    key = standardise_key(key)

    def wrapper(func: Callable) -> Callable:
        logger.info(f"registering write fn {key = } {func = }")
        WRITE_FNS[key] = func
        return func

    return wrapper


def standardise_key(key: Hashable) -> Hashable:
    return key.strip().lower() if isinstance(key, str) else key
