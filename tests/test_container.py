from __future__ import annotations

from pathlib import Path

import pytest

from io_adapters import (
    add_domain,
    get_fake_adapter,
    get_real_adapter,
    register_domain_read_fn,
    register_domain_write_fn,
)


@pytest.mark.parametrize(
    ("domain", "expected_read_fns", "expected_write_fns"),
    [pytest.param("orders", ["str"], []), pytest.param("payment", [], ["json", "str"])],
)
def test_container(domain, expected_read_fns, expected_write_fns):
    add_domain("orders")

    @register_domain_read_fn("orders", "str")
    def read_str(path: str | Path, **kwargs: dict) -> str:
        return ""

    add_domain("payment")

    @register_domain_write_fn("payment", "str")
    def write_str(data: dict, path: str | Path, **kwargs: dict) -> None:
        pass

    @register_domain_write_fn("payment", "json")
    def write_json(data: dict, path: str | Path, **kwargs: dict) -> None:
        pass

    assert sorted(get_real_adapter(domain).read_fns.keys()) == expected_read_fns
    assert sorted(get_real_adapter(domain).read_fns.keys()) == sorted(
        get_fake_adapter(domain).read_fns.keys()
    )

    assert sorted(get_real_adapter(domain).write_fns.keys()) == expected_write_fns
    assert sorted(get_real_adapter(domain).write_fns.keys()) == sorted(
        get_fake_adapter(domain).write_fns.keys()
    )
