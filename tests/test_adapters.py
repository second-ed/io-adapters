import operator
import shutil
from contextlib import nullcontext
from pathlib import Path

import pytest
from returns.result import Success, safe

from src.io_adapters import FakeAdapter, RealAdapter
from src.io_adapters._adapters import _apply_decs

REPO_ROOT = Path(__file__).parents[1]
MOCK_DATA_PATH = f"{REPO_ROOT}/tests/mock_data/mock.json"
FILES = ("__init__.py", "mock.csv", "reqs.txt", "main.py")
TMP_ROOT = REPO_ROOT.joinpath("tests", "tmp_mock_data")
INITIAL_FILES = [TMP_ROOT.joinpath(x) for x in FILES]


@pytest.fixture(autouse=True)
def setup():
    for f in INITIAL_FILES:
        f.parent.mkdir(parents=True, exist_ok=True)
        f.joinpath(f).touch()

    yield

    shutil.rmtree(TMP_ROOT)


ADAPTERS = [
    pytest.param(RealAdapter(), id="using a RealAdapter"),
    pytest.param(
        FakeAdapter(files=dict.fromkeys(map(str, INITIAL_FILES), "")), id="using a FakeAdapter"
    ),
]


@pytest.mark.parametrize(
    ("adapter", "data", "file_type"),
    [
        pytest.param(RealAdapter, {"a": 0, "b": 1, "c": [2, 3]}, "json"),
        pytest.param(FakeAdapter, {"a": 0, "b": 1, "c": [2, 3]}, "json"),
    ],
)
def test_adapter(adapter, data, file_type):
    io = adapter()
    io.write(data, MOCK_DATA_PATH, file_type)
    assert io.read(MOCK_DATA_PATH, file_type) == data


@pytest.mark.parametrize(
    ("file_type", "expected_context"),
    [
        pytest.param("json", nullcontext()),
        pytest.param("invalid", pytest.raises(NotImplementedError)),
    ],
)
def test_raises_when_given_invalid_read_file_type(file_type, expected_context):
    with expected_context:
        RealAdapter().read(MOCK_DATA_PATH, file_type)


@pytest.mark.parametrize(
    ("file_type", "expected_context"),
    [
        pytest.param("json", nullcontext()),
        pytest.param("invalid", pytest.raises(NotImplementedError)),
    ],
)
def test_raises_when_given_invalid_write_file_type(file_type, expected_context):
    with expected_context:
        FakeAdapter().write({"a": 0}, MOCK_DATA_PATH, file_type)


@pytest.mark.parametrize(
    ("path", "expected_context"),
    [
        pytest.param(MOCK_DATA_PATH, nullcontext()),
        pytest.param("invalid", pytest.raises(FileNotFoundError)),
    ],
)
def test_raises_when_given_invalid_file_path(path, expected_context):
    with expected_context:
        FakeAdapter(files={MOCK_DATA_PATH: {"a": 0}}).read(path, "json")


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


@pytest.mark.parametrize("adapter", ADAPTERS)
@pytest.mark.parametrize(
    ("path", "glob_pattern", "expected_result"),
    [
        pytest.param(
            TMP_ROOT,
            "*",
            [
                Path(f"{TMP_ROOT}/__init__.py").resolve(),
                Path(f"{TMP_ROOT}/main.py").resolve(),
                Path(f"{TMP_ROOT}/mock.csv").resolve(),
                Path(f"{TMP_ROOT}/reqs.txt").resolve(),
            ],
            id="get all files",
        ),
        pytest.param(
            TMP_ROOT,
            "*.py",
            [Path(f"{TMP_ROOT}/__init__.py").resolve(), Path(f"{TMP_ROOT}/main.py").resolve()],
            id="glob .py files",
        ),
    ],
)
def test_list_files(adapter, path, glob_pattern, expected_result):
    assert adapter.list_files(path, glob_pattern) == expected_result


@pytest.mark.parametrize("adapter", ADAPTERS)
@pytest.mark.parametrize(
    ("old", "new"),
    [
        pytest.param(
            f"{TMP_ROOT}/__init__.py",
            f"{TMP_ROOT}/new_init.py",
            id="both old and new exist after copy",
        ),
    ],
)
def test_copy_file(adapter, old, new):
    adapter.copy_file(old, new)
    assert adapter.exists(old)
    assert adapter.exists(new)


@pytest.mark.parametrize("adapter", ADAPTERS)
@pytest.mark.parametrize(
    ("old", "new"),
    [
        pytest.param(
            f"{TMP_ROOT}/__init__.py",
            f"{TMP_ROOT}/new_init.py",
            id="old not exists and new exists after move",
        ),
    ],
)
def test_move_file(adapter, old, new):
    adapter.move_file(old, new)
    assert not adapter.exists(old)
    assert adapter.exists(new)


@pytest.mark.parametrize("adapter", ADAPTERS)
@pytest.mark.parametrize(
    ("path", "missing_ok", "expected_context"),
    [
        pytest.param(
            f"{TMP_ROOT}/__init__.py",
            True,
            nullcontext(),
            id="file is deleted after delete",
        ),
        pytest.param(
            f"{TMP_ROOT}/INVALID_FILE.py",
            False,
            pytest.raises(FileNotFoundError),
            id="raises error if missing_ok is False",
        ),
    ],
)
def test_delete_file(adapter, path, missing_ok, expected_context):
    with expected_context:
        adapter.delete_file(path, missing_ok=missing_ok)
        assert not adapter.exists(path)


@pytest.mark.parametrize("adapter", ADAPTERS)
def test_write_then_list(adapter):
    adapter.write(
        {"a": 0, "b": 1}, f"{TMP_ROOT}/pending/20260425_211300_000.json", "json", default=str
    )
    assert adapter.list_files(f"{TMP_ROOT}/pending") == [
        Path(f"{TMP_ROOT}/pending/20260425_211300_000.json")
    ]


def test_apply_decs() -> None:
    def append(lst: list[int], value: int):
        def wrapper(fn):
            lst.append(value)
            return fn

        return wrapper

    dec_lst, fn_lst = [], []

    @append(dec_lst, 1)
    @append(dec_lst, 2)
    def blah():
        return None

    _apply_decs(fn=lambda x: x, decs=(append(fn_lst, 1), append(fn_lst, 2)))

    assert dec_lst == fn_lst


@safe
def safe_read_py_file(path: str) -> str:
    return Path(path).read_text()


def read_py_file(path: str) -> str:
    return Path(path).read_text()


SAFE_FNS = {"safe_py": safe_read_py_file, "py": read_py_file}


@pytest.mark.parametrize(
    ("adapter", "file_type", "expected_result"),
    [
        pytest.param(
            RealAdapter(read_fns=SAFE_FNS),
            "safe_py",
            Success(""),
            id="reads file with monad using a RealAdapter",
        ),
        pytest.param(
            RealAdapter(read_fns=SAFE_FNS), "py", "", id="reads file normally using a RealAdapter"
        ),
        pytest.param(
            FakeAdapter(
                files=dict.fromkeys(map(str, INITIAL_FILES), ""),
                read_fns=SAFE_FNS,
                read_decs=[safe],
            ),
            "safe_py",
            Success(""),
            id="reads file with monad using a FakeAdapter",
        ),
        pytest.param(
            FakeAdapter(
                files=dict.fromkeys(map(str, INITIAL_FILES), ""),
                read_fns=SAFE_FNS,
            ),
            "py",
            "",
            id="reads file normally using a FakeAdapter",
        ),
    ],
)
def test_adapters_with_decs(adapter, file_type, expected_result):
    assert adapter.read(INITIAL_FILES[0], file_type) == expected_result
