from __future__ import annotations

import logging
from collections.abc import Callable
from pathlib import Path
from typing import Concatenate, ParamSpec, TypeAlias

logger = logging.getLogger(__name__)

Data: TypeAlias = "Data"
P = ParamSpec("P")

ReadFn = Callable[Concatenate[str | Path, P], Data]
WriteFn = Callable[Concatenate[Data, str | Path, P], None]


READ_FNS: dict[str, ReadFn] = {}
WRITE_FNS: dict[str, WriteFn] = {}


def register_read_fn(key: str) -> Callable:
    key = key.strip().lower()

    def wrapper(func: Callable) -> Callable:
        logger.info(f"registering read fn {key = } {func = }")
        READ_FNS[key] = func
        return func

    return wrapper


def register_write_fn(key: str) -> Callable:
    key = key.strip().lower()

    def wrapper(func: Callable) -> Callable:
        logger.info(f"registering write fn {key = } {func = }")
        WRITE_FNS[key] = func
        return func

    return wrapper
