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
    """
    return DEFAULT_CONTAINER.add_domain(domain)


def register_domain_read_fn(domain: Hashable | list[Hashable], key: Hashable) -> Callable:
    return DEFAULT_CONTAINER.register_read_fn(domain, key)


def register_domain_write_fn(domain: Hashable, key: Hashable) -> Callable:
    return DEFAULT_CONTAINER.register_write_fn(domain, key)


def get_real_adapter(domain: Hashable) -> RealAdapter:
    return DEFAULT_CONTAINER.get_real_adapter(domain)


def get_fake_adapter(domain: Hashable, files: dict | None = None) -> RealAdapter:
    return DEFAULT_CONTAINER.get_fake_adapter(domain, files)
