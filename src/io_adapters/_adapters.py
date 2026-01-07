from __future__ import annotations

import datetime
import logging
from collections.abc import Callable, Hashable
from pathlib import Path
from types import MappingProxyType

import attrs
from attrs.validators import deep_mapping, instance_of, is_callable, optional

from io_adapters._clock import default_datetime, default_guid, fake_datetime, fake_guid
from io_adapters._registries import READ_FNS, WRITE_FNS, Data, ReadFn, WriteFn, standardise_key

logger = logging.getLogger(__name__)


@attrs.define
class IoAdapter:
    read_fns: MappingProxyType[Hashable, ReadFn] = attrs.field(
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
    write_fns: MappingProxyType[Hashable, WriteFn] = attrs.field(
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
    guid_fn: Callable[[], str] = attrs.field(default=None, validator=optional(is_callable()))
    datetime_fn: Callable[[], datetime.datetime] = attrs.field(
        default=None, validator=optional(is_callable())
    )

    def read(self, path: str | Path, file_type: Hashable, **kwargs: dict) -> Data:
        """Read `path` using the registered function for `file_type`.

        Raises:
            NotImplementedError: If the given `file_type` does not have a registered function.

        Usage
        -----

        Here the ``read_json`` function is registered with the ``register_read_fn`` decorator.

        Then when the ``adapter`` object calls ``read`` with the ``"json"`` ``file_type`` it will use the registered function.

        The ``key`` used to register the function doesn't have to be a string, as long as it's ``Hashable`` it can be used.

        .. code-block:: python

            from io_adapters import RealAdapter, register_read_fn

            @register_read_fn("json")
            def read_json(path: str | Path, **kwargs: dict) -> dict:
                return json.loads(Path(path).read_text(), **kwargs)

            adapter = RealAdapter()
            data = adapter.read("some/path/to/file.json", "json")

        """
        logger.info(f"{path = } {file_type = } {kwargs = }")
        file_type = standardise_key(file_type)

        if file_type not in self.read_fns:
            msg = f"`read` is not implemented for {file_type}"
            logger.error(msg)
            raise NotImplementedError(msg)
        return self.read_fns[file_type](path, **kwargs)

    def write(self, data: Data, path: str | Path, file_type: Hashable, **kwargs: dict) -> None:
        """Write `data` to `path` using the registered function for `file_type`.

        Raises:
            NotImplementedError: If the given `file_type` does not have a registered function.

        Usage
        -----

        Here the ``write_json`` function is registered with the ``register_write_fn`` decorator.

        Then when the ``adapter`` object calls ``write`` with the ``WriteFormat.JSON`` ``file_type`` it will use the registered function.

        .. code-block:: python

            from enum import Enum
            from io_adapters import RealAdapter, register_write_fn

            class WriteFormat(Enum):
                JSON = "json"

            @register_write_fn(WriteFormat.JSON)
            def write_json(data: dict, path: str | Path, **kwargs: dict) -> None:
                path = Path(path)
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_text(json.dumps(data, **kwargs))

            adapter = RealAdapter()
            adapter.write({"a": 1}, "some/path/to/file.json", WriteFormat.JSON)

            fake_adapter = FakeAdapter()
            fake_adapter.write({"a": 1}, "some/path/to/file.json", WriteFormat.JSON)


        The interfaces between the ``FakeAdapter`` and the ``RealAdapter`` means that the two can be passed in interchangeably, making testing much easier

        .. code-block:: python

            def some_usecase(adapter: IoAdapter, path: str) -> None:
                # Some business logic

                adapter.write({"a": 1}, path, WriteFormat.JSON)

            # in production inject the real adapter
            some_usecase(RealAdapter(), "some/path/to/file.json")

            # in testing inject the fake and assert that the fakes end state is as expected
            fake = FakeAdapter()
            some_usecase(fake, "some/path/to/file.json")
            assert fake.files["some/path/to/file.json"] == {"a": 1}

        """
        logger.info(f"{path = } {file_type = } {kwargs = }")
        file_type = standardise_key(file_type)

        if file_type not in self.write_fns:
            msg = f"`write` is not implemented for {file_type}"
            logger.error(msg)
            raise NotImplementedError(msg)
        return self.write_fns[file_type](data, path, **kwargs)

    def get_guid(self) -> str:
        return self.guid_fn()

    def get_datetime(self) -> datetime.datetime:
        return self.datetime_fn()


@attrs.define
class RealAdapter(IoAdapter):
    def __attrs_post_init__(self) -> None:
        self.guid_fn = self.guid_fn or default_guid
        self.datetime_fn = self.datetime_fn or default_datetime


@attrs.define
class FakeAdapter(IoAdapter):
    files: dict[str, Data] = attrs.field(factory=dict, validator=instance_of(dict))

    def __attrs_post_init__(self) -> None:
        self.read_fns = MappingProxyType(dict.fromkeys(self.read_fns.keys(), self._read_fn))
        self.write_fns = MappingProxyType(dict.fromkeys(self.write_fns.keys(), self._write_fn))
        self.guid_fn = self.guid_fn or fake_guid
        self.datetime_fn = self.datetime_fn or fake_datetime

    def _read_fn(self, path: str) -> Data:
        try:
            return self.files[path]
        except KeyError as e:
            raise FileNotFoundError(f"{path = } {self.files = }") from e

    def _write_fn(self, data: Data, path: str) -> None:
        self.files[str(path)] = data

    def get_guid(self) -> str:
        return self.guid_fn()

    def get_datetime(self) -> datetime.datetime:
        return self.datetime_fn()
