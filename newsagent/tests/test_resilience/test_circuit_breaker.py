import pytest

from newsagent.resilience.circuit_breaker import CircuitBreaker


class TestCircuitBreaker:
    def test_initial_state_closed(self) -> None:
        cb = CircuitBreaker()
        assert cb.state == "closed"

    def test_record_failure_opens_on_threshold(self) -> None:
        cb = CircuitBreaker(failure_threshold=3, reset_timeout=60.0)
        cb.record_failure()
        assert cb.state == "closed"
        cb.record_failure()
        assert cb.state == "closed"
        cb.record_failure()
        assert cb.state == "open"

    def test_record_success_resets(self) -> None:
        cb = CircuitBreaker(failure_threshold=2, reset_timeout=60.0)
        cb.record_failure()
        cb.record_failure()
        assert cb.state == "open"
        cb.record_success()
        assert cb.state == "closed"
        assert cb._failure_count == 0

    def test_half_open_after_timeout(self) -> None:
        cb = CircuitBreaker(failure_threshold=1, reset_timeout=-1.0)
        cb.record_failure()
        assert cb.state == "half-open"

    def test_half_open_success_transitions_to_closed(self) -> None:
        cb = CircuitBreaker(failure_threshold=1, reset_timeout=0.0)
        cb.record_failure()
        cb._last_failure_time = 0.0
        assert cb.state == "half-open"
        cb.record_success()
        assert cb.state == "closed"

    def test_initial_last_failure_time_none(self) -> None:
        cb = CircuitBreaker()
        assert cb._last_failure_time is None
        assert cb.state == "closed"

    @pytest.mark.asyncio
    async def test_decorator_blocks_when_open(self) -> None:
        cb = CircuitBreaker(failure_threshold=1, reset_timeout=60.0)

        @cb
        async def fail_func() -> str:
            raise ValueError("fail")

        with pytest.raises(ValueError):
            await fail_func()

        with pytest.raises(RuntimeError, match="Circuit breaker is open"):
            await fail_func()

    @pytest.mark.asyncio
    async def test_decorator_success_resets(self) -> None:
        cb = CircuitBreaker(failure_threshold=1, reset_timeout=60.0)

        @cb
        async def ok_func() -> str:
            return "ok"

        result = await ok_func()
        assert result == "ok"
        assert cb.state == "closed"

    @pytest.mark.asyncio
    async def test_decorator_opens_after_multiple_failures(self) -> None:
        cb = CircuitBreaker(failure_threshold=2, reset_timeout=60.0)

        @cb
        async def fail_func() -> str:
            raise ValueError("fail")

        with pytest.raises(ValueError):
            await fail_func()
        assert cb.state == "closed"

        with pytest.raises(ValueError):
            await fail_func()
        assert cb.state == "open"
