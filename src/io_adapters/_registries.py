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


READ_FNS: dict[str, ReadFn] = {}
WRITE_FNS: dict[str, WriteFn] = {}


def register_read_fn(key: Hashable) -> Callable:
    key = standardise_key(key)

    def wrapper(func: Callable) -> Callable:
        logger.info(f"registering read fn {key = } {func = }")
        READ_FNS[key] = func
        return func

    return wrapper


def register_write_fn(key: Hashable) -> Callable:
    key = standardise_key(key)

    def wrapper(func: Callable) -> Callable:
        logger.info(f"registering write fn {key = } {func = }")
        WRITE_FNS[key] = func
        return func

    return wrapper


def standardise_key(key: Hashable) -> Hashable:
    return key.strip().lower() if isinstance(key, str) else key
