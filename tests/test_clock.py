import hypothesis.strategies as st
from hypothesis import given

from src.io_adapters._clock import FakeClock


@given(initial_datetimes=st.lists(st.datetimes()))
def test_fake_clock_returns_datetimes_in_order(initial_datetimes) -> None:
    clock = FakeClock(initial_datetimes.copy())

    assert [clock.now() for _ in initial_datetimes] == initial_datetimes
