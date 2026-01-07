from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from io_adapters._registries import register_read_fn, register_write_fn


@register_read_fn("json")
def read_json(path: str | Path, **kwargs: dict[str, Any]) -> dict:
    return json.loads(Path(path).read_text(), **kwargs)


@register_write_fn("json")
def write_json(data: dict, path: str | Path, **kwargs: dict[str, Any]) -> None:
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, **kwargs))
