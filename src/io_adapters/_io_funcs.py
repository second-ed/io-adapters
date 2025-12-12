from __future__ import annotations

import json
from pathlib import Path

import tomllib

from io_adapters._registries import register_read_fn, register_write_fn


@register_read_fn("json")
def read_json(path: str | Path, **kwargs: dict) -> dict:
    return json.loads(Path(path).read_text(), **kwargs)


@register_write_fn("json")
def write_json(data: dict, path: str | Path, **kwargs: dict) -> None:
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, **kwargs))


@register_read_fn("toml")
def read_toml(path: str | Path, **kwargs: dict) -> dict:
    return tomllib.loads(Path(path).read_text(), **kwargs)


@register_write_fn("toml")
def write_toml(data: dict, path: str | Path, **kwargs: dict) -> None:
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(tomllib.dumps(data, **kwargs))
