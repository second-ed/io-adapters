from __future__ import annotations

import logging
from collections.abc import Callable, Hashable, Iterable
from enum import Enum, auto

import attrs
from attrs.validators import deep_iterable, instance_of

from io_adapters import FakeAdapter, RealAdapter
from io_adapters._registries import standardise_key

logger = logging.getLogger(__name__)


class _FnType(Enum):
    READ = auto()
    WRITE = auto()


@attrs.define
class Container:
    domains: Iterable = attrs.field(validator=deep_iterable(member_validator=instance_of(Hashable)))
    domain_fns: dict[Hashable, dict[Hashable, Callable]] = attrs.field(init=False)

    def __attrs_post_init__(self) -> None:
        self.domain_fns = {domain: {_FnType.READ: {}, _FnType.WRITE: {}} for domain in self.domains}

    def add_domain(self, domain: Hashable) -> None:
        self.domain_fns[domain] = {_FnType.READ: {}, _FnType.WRITE: {}}

    def register_read_fn(self, domain: Hashable, key: Hashable) -> Callable:
        domain = standardise_key(domain)
        key = standardise_key(key)

        def wrapper(func: Callable) -> Callable:
            logger.info(f"registering read fn {key = } {func = }")
            self.domain_fns[domain][_FnType.READ][key] = func
            return func

        return wrapper

    def register_write_fn(self, domain: Hashable, key: Hashable) -> Callable:
        domain = standardise_key(domain)
        key = standardise_key(key)

        def wrapper(func: Callable) -> Callable:
            logger.info(f"registering read fn {key = } {func = }")
            self.domain_fns[domain][_FnType.WRITE][key] = func
            return func

        return wrapper

    def get_real_adapter(self, domain: Hashable) -> RealAdapter:
        return RealAdapter(
            read_fns=self.domain_fns[domain][_FnType.READ],
            write_fns=self.domain_fns[domain][_FnType.WRITE],
        )

    def get_fake_adapter(self, domain: Hashable, files: dict | None = None) -> RealAdapter:
        return FakeAdapter(
            read_fns=self.domain_fns[domain][_FnType.READ],
            write_fns=self.domain_fns[domain][_FnType.WRITE],
            files=files or {},
        )


DEFAULT_CONTAINER = Container(domains=[])


def add_domain(domain: Hashable) -> None:
    """Add a domain to the default ``Container``

    .. code-block:: python

        from io_adapters import add_domain

        add_domain("orders")

    The ``orders`` domain is now added to the default ``Container`` and can have IO functions registered to it.

    Relying on deliberate registering of a domain avoids situations where a typo could register a function to a non-existent domain: e.g. ``'ordesr'`` instead of the intended ``'orders'``.
    """
    return DEFAULT_CONTAINER.add_domain(domain)


def register_domain_read_fn(domain: Hashable, key: Hashable) -> Callable:
    """Register a read function to a domain in the default ``Container``.

    Decorators can be stacked to register the same function to multiple domains.

    .. code-block:: python

        from io_adapters import add_domain, register_domain_read_fn

        add_domain("orders")

        @register_domain_read_fn("orders", "str")
        def read_str(path: str | Path, **kwargs: dict) -> str:
            ...

        add_domain("payment")

        @register_domain_read_fn("orders", "json")
        @register_domain_read_fn("payment", "json")
        def read_json(path: str | Path, **kwargs: dict) -> dict:
            ...
    """
    return DEFAULT_CONTAINER.register_read_fn(domain, key)


def register_domain_write_fn(domain: Hashable, key: Hashable) -> Callable:
    """Register a write function to a domain in the default ``Container``.

    Decorators can be stacked to register the same function to multiple domains.

    .. code-block:: python

        from io_adapters import add_domain, register_domain_write_fn

        add_domain("orders")

        @register_domain_write_fn("orders", "str")
        def write_str(data: dict, path: str | Path, **kwargs: dict) -> None:
            ...

        add_domain("payment")

        @register_domain_write_fn("orders", "json")
        @register_domain_write_fn("payment", "json")
        def write_json(data: dict, path: str | Path, **kwargs: dict) -> None:
            ...
    """
    return DEFAULT_CONTAINER.register_write_fn(domain, key)


def get_real_adapter(domain: Hashable) -> RealAdapter:
    """Get a ``RealAdapter`` for the given domain.

    The returned adapter will have all of the functions registered to that domain.

    .. code-block:: python

        from io_adapters import RealAdapter, get_real_adapter

        orders_adapter: RealAdapter = get_real_adapter("orders")

    The ``RealAdapter`` that is assigned to the ``orders_adapter`` variable will have all of the registered read and write I/O functions.

    """
    return DEFAULT_CONTAINER.get_real_adapter(domain)


def get_fake_adapter(domain: Hashable, files: dict | None = None) -> FakeAdapter:
    """Get a ``FakeAdapter`` for the given domain.

    The returned adapter will have all of the functions registered to that domain.

    .. code-block:: python

        from io_adapters import FakeAdapter, get_fake_adapter

        orders_adapter: FakeAdapter = get_fake_adapter("orders")

    The ``FakeAdapter`` that is assigned to the ``orders_adapter`` variable will have fake representations for all of the registered read and write I/O functions.

    This can optionally be given a dictionary of files to setup the initial state for testing. An example of how this could be used is below:

    .. code-block:: python

        from io_adapters import FakeAdapter, get_fake_adapter

        starting_files = {"path/to/data.json": {"a": 0, "b": 1}}

        orders_adapter: FakeAdapter = get_fake_adapter("orders", starting_files)

        some_orders_usecase(adapter=orders_adapter, data_path="path/to/data.json")

        assert orders_adapter.files["path/to/modified_data.json"] == {"a": 1, "b": 2}

    """
    return DEFAULT_CONTAINER.get_fake_adapter(domain, files)
