from io_adapters._adapters import FakeAdapter, IoAdapter, RealAdapter
from io_adapters._container import (
    Container,
    add_domain,
    get_fake_adapter,
    get_real_adapter,
    register_domain_read_fn,
    register_domain_write_fn,
)
from io_adapters._io_funcs import read_json, write_json

__all__ = [
    "Container",
    "FakeAdapter",
    "IoAdapter",
    "RealAdapter",
    "add_domain",
    "get_fake_adapter",
    "get_real_adapter",
    "read_json",
    "register_domain_read_fn",
    "register_domain_write_fn",
    "write_json",
]
