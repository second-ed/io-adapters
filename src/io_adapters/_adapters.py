from __future__ import annotations

import datetime
import logging
from abc import ABC, abstractmethod
from collections.abc import Hashable
from pathlib import Path
from types import MappingProxyType
from uuid import uuid4

import attrs
from attrs.validators import instance_of

from io_adapters._registries import READ_FNS, WRITE_FNS, Data

logger = logging.getLogger(__name__)


@attrs.define
class IoAdapter(ABC):
    _read_fns: MappingProxyType = attrs.field(
        default=READ_FNS, validator=instance_of(MappingProxyType), converter=MappingProxyType
    )
    _write_fns: MappingProxyType = attrs.field(
        default=WRITE_FNS, validator=instance_of(MappingProxyType), converter=MappingProxyType
    )

    def read(self, path: str | Path, file_type: str, **kwargs: dict) -> Data:
        logger.info(f"{path = } {file_type = } {kwargs = }")
        file_type = self._standardise_str(file_type)

        if file_type not in self._read_fns:
            msg = f"`read` is not implemented for {file_type}"
            logger.error(msg)
            raise NotImplementedError(msg)
        return self._read_fns[file_type](path, **kwargs)

    def write(self, data: Data, path: str | Path, file_type: str, **kwargs: dict) -> None:
        logger.info(f"{path = } {file_type = } {kwargs = }")
        file_type = self._standardise_str(file_type)

        if file_type not in self._write_fns:
            msg = f"`write` is not implemented for {file_type}"
            logger.error(msg)
            raise NotImplementedError(msg)
        return self._write_fns[file_type](data, path, **kwargs)

    def _standardise_str(self, file_type: Hashable) -> Hashable:
        return file_type.lower().strip() if isinstance(file_type, str) else file_type

    @abstractmethod
    def get_guid(self) -> str: ...

    @abstractmethod
    def get_datetime(self) -> datetime.datetime: ...


@attrs.define
class RealAdapter(IoAdapter):
    def get_guid(self) -> str:
        return str(uuid4())

    def get_datetime(self) -> datetime.datetime:
        return datetime.datetime.now(datetime.UTC)


@attrs.define
class FakeAdapter(IoAdapter):
    files: dict[str, Data] = attrs.field(factory=dict, validator=instance_of(dict))

    def __attrs_post_init__(self) -> None:
        self._read_fns = MappingProxyType(dict.fromkeys(READ_FNS, self._read_fn))
        self._write_fns = MappingProxyType(dict.fromkeys(WRITE_FNS, self._write_fn))

    def _read_fn(self, path: str) -> Data:
        try:
            return self.files[path]
        except KeyError as e:
            raise FileNotFoundError(f"{path = } {self.files = }") from e

    def _write_fn(self, data: Data, path: str) -> None:
        self.files[str(path)] = data

    def get_guid(self) -> str:
        return "abc-123"

    def get_datetime(self) -> datetime.datetime:
        return datetime.datetime(2025, 1, 1, 12, tzinfo=datetime.UTC)
