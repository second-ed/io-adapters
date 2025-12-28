from __future__ import annotations

import datetime
import logging
from abc import ABC, abstractmethod
from collections.abc import Hashable
from pathlib import Path
from types import MappingProxyType
from uuid import uuid4

import attrs
from attrs.validators import deep_mapping, instance_of, is_callable

from io_adapters._registries import READ_FNS, WRITE_FNS, Data, standardise_key

logger = logging.getLogger(__name__)


@attrs.define
class IoAdapter(ABC):
    read_fns: MappingProxyType = attrs.field(
        default=READ_FNS,
        validator=[
            deep_mapping(
                key_validator=instance_of(Hashable),
                value_validator=is_callable(),
                mapping_validator=instance_of(MappingProxyType),
            )
        ],
        converter=MappingProxyType,
    )
    write_fns: MappingProxyType = attrs.field(
        default=WRITE_FNS,
        validator=[
            deep_mapping(
                key_validator=instance_of(Hashable),
                value_validator=is_callable(),
                mapping_validator=instance_of(MappingProxyType),
            )
        ],
        converter=MappingProxyType,
    )

    def read(self, path: str | Path, file_type: str, **kwargs: dict) -> Data:
        logger.info(f"{path = } {file_type = } {kwargs = }")
        file_type = standardise_key(file_type)

        if file_type not in self.read_fns:
            msg = f"`read` is not implemented for {file_type}"
            logger.error(msg)
            raise NotImplementedError(msg)
        return self.read_fns[file_type](path, **kwargs)

    def write(self, data: Data, path: str | Path, file_type: str, **kwargs: dict) -> None:
        logger.info(f"{path = } {file_type = } {kwargs = }")
        file_type = standardise_key(file_type)

        if file_type not in self.write_fns:
            msg = f"`write` is not implemented for {file_type}"
            logger.error(msg)
            raise NotImplementedError(msg)
        return self.write_fns[file_type](data, path, **kwargs)

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
        self.read_fns = MappingProxyType(dict.fromkeys(self.read_fns.keys(), self._read_fn))
        self.write_fns = MappingProxyType(dict.fromkeys(self.write_fns.keys(), self._write_fn))

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
