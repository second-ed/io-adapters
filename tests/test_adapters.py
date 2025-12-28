import operator
from contextlib import nullcontext
from pathlib import Path

import pytest

from src.io_adapters import FakeAdapter, RealAdapter

REPO_ROOT = Path(__file__).parents[1]


@pytest.mark.parametrize(
    ("adapter", "data", "file_type"),
    [
        pytest.param(RealAdapter, {"a": 0, "b": 1, "c": [2, 3]}, "json"),
        pytest.param(FakeAdapter, {"a": 0, "b": 1, "c": [2, 3]}, "json"),
    ],
)
def test_adapter(adapter, data, file_type):
    path = f"{REPO_ROOT}/tests/mock_data/mock.json"
    io = adapter()
    io.write(data, path, file_type)
    assert io.read(path, file_type) == data


@pytest.mark.parametrize(
    ("file_type", "expected_context"),
    [
        pytest.param("json", nullcontext()),
        pytest.param("invalid", pytest.raises(NotImplementedError)),
    ],
)
def test_raises_when_given_invalid_read_file_type(file_type, expected_context):
    with expected_context:
        path = f"{REPO_ROOT}/tests/mock_data/mock.json"
        RealAdapter().read(path, file_type)


@pytest.mark.parametrize(
    ("file_type", "expected_context"),
    [
        pytest.param("json", nullcontext()),
        pytest.param("invalid", pytest.raises(NotImplementedError)),
    ],
)
def test_raises_when_given_invalid_write_file_type(file_type, expected_context):
    with expected_context:
        path = f"{REPO_ROOT}/tests/mock_data/mock.json"
        FakeAdapter().write({"a": 0}, path, file_type)


@pytest.mark.parametrize(
    ("path", "expected_context"),
    [
        pytest.param(f"{REPO_ROOT}/tests/mock_data/mock.json", nullcontext()),
        pytest.param("invalid", pytest.raises(FileNotFoundError)),
    ],
)
def test_raises_when_given_invalid_file_path(path, expected_context):
    with expected_context:
        FakeAdapter(files={f"{REPO_ROOT}/tests/mock_data/mock.json": {"a": 0}}).read(path, "json")


@pytest.mark.parametrize(
    ("adapter", "op"),
    [pytest.param(RealAdapter, operator.ne), pytest.param(FakeAdapter, operator.eq)],
)
def test_guid(adapter, op):
    assert op(adapter().get_guid(), adapter().get_guid())


@pytest.mark.parametrize(
    ("adapter", "op"),
    [pytest.param(RealAdapter, operator.ne), pytest.param(FakeAdapter, operator.eq)],
)
def test_datetime(adapter, op):
    assert op(adapter().get_datetime(), adapter().get_datetime())
