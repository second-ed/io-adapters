# io-adapters
A small utility library for decoupling I/O from business logic by combining
dependency injection with lightweight, automatically generated fakes.

### Install
```shell
uv add io-adapters
```

### API Reference

[io-adapters API docs](https://second-ed.github.io/io-adapters/)

Testing use cases that involve I/O is inherently difficult because they depend on:

- external state (filesystems, databases, services)

- side effects that are hard to observe directly

- slow or flaky infrastructure

A common mitigation is to combine:

- Dependency Injection (DI)

- The Repository / Adapter pattern

This allows business logic to depend on an abstract interface rather than concrete I/O.

However, in practice this usually requires:

- writing and maintaining bespoke fake implementations

- keeping fake behaviour in sync with real implementations

- duplicating boilerplate across domains

For small or medium-sized projects, this overhead can outweigh the benefits.

 Simply register each I/O function with one of the register decorators and the functionality will be added to the `RealAdapter` object, on top of that a stub will be added to the `FakeAdapter` object too so you can pass in either to your usecase and the functionality will work.

### Example

```python
from enum import Enum
from pathlib import Path

from io_adapters import (
    IoAdapter,
    RealAdapter,
    add_domain,
    get_fake_adapter,
    get_real_adapter,
    register_domain_read_fn,
    register_domain_write_fn,
)


# you can use any hashable object to register an I/O function
class FileFormat(Enum):
    JSON = "json"


add_domain("orders")
add_domain("payment")


@register_domain_read_fn("orders", "str")
def read_str(path: str | Path, **kwargs: dict) -> str: ...


# stack decorators to register the same function to multiple domains
@register_domain_read_fn("orders", FileFormat.JSON)
@register_domain_read_fn("payment", FileFormat.JSON)
def read_json(path: str | Path, **kwargs: dict) -> dict: ...


@register_domain_write_fn("orders", "str")
def write_str(data: dict, path: str | Path, **kwargs: dict) -> None: ...


@register_domain_write_fn("orders", FileFormat.JSON)
@register_domain_write_fn("payment", FileFormat.JSON)
def write_json(data: dict, path: str | Path, **kwargs: dict) -> None: ...


def some_usecase(adapter: IoAdapter, path: str) -> None:
    adapter.read(path, "str")
    # Some business logic
    new_path = f"{path}_new.json"

    adapter.write({"a": 1}, new_path, FileFormat.JSON)


# in production inject the real adapter
orders_adapter: RealAdapter = get_real_adapter("orders")
some_usecase(orders_adapter, "some/path/to/file.json")


# in testing inject the fake which has all the same funcitonality as the 
# `RealAdapter` and assert that the fakes end state is as expected
fake = get_fake_adapter("orders")
some_usecase(fake, "some/path/to/file.json")
assert fake.files["some/path/to/file.json"] == {"a": 1}
```


# Repo map
```
├── .github
│   └── workflows
│       ├── ci_tests.yaml
│       └── publish.yaml
├── .pytest_cache
│   └── README.md
├── docs
│   └── source
│       └── conf.py
├── src
│   └── io_adapters
│       ├── __init__.py
│       ├── _adapters.py
│       ├── _clock.py
│       ├── _container.py
│       ├── _io_funcs.py
│       └── _registries.py
├── tests
│   ├── __init__.py
│   ├── test_adapters.py
│   ├── test_adapters_apis.py
│   └── test_container.py
├── .pre-commit-config.yaml
├── README.md
├── pyproject.toml
├── ruff.toml
└── uv.lock
::
```