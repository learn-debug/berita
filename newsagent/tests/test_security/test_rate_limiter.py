import time

import pytest

from newsagent.security.rate_limiter import RateLimiter


class TestAcquire:
    def test_acquire_returns_true_within_limit(self) -> None:
        rl = RateLimiter(max_calls=5, window=60.0)
        assert rl.acquire()
        assert len(rl._calls) == 1

    def test_acquire_records_call(self) -> None:
        rl = RateLimiter(max_calls=5, window=60.0)
        rl.acquire()
        rl.acquire()
        rl.acquire()
        assert len(rl._calls) == 3

    def test_acquire_blocks_when_exceeded(self) -> None:
        rl = RateLimiter(max_calls=2, window=60.0)
        assert rl.acquire()
        assert rl.acquire()
        assert not rl.acquire()
        assert len(rl._calls) == 2

    def test_acquire_exactly_at_limit(self) -> None:
        rl = RateLimiter(max_calls=3, window=60.0)
        assert rl.acquire()
        assert rl.acquire()
        assert rl.acquire()
        assert not rl.acquire()

    def test_acquire_prunes_old_calls(self) -> None:
        rl = RateLimiter(max_calls=2, window=0.001)
        now = time.monotonic()
        rl._calls = [now - 10, now - 10]
        assert rl.acquire()
        assert len(rl._calls) == 1

    def test_acquire_zero_window(self) -> None:
        rl = RateLimiter(max_calls=2, window=0.0)
        assert rl.acquire()
        assert rl.acquire()
        assert rl.acquire()


class TestAllow:
    def test_within_limit(self) -> None:
        rl = RateLimiter(max_calls=5, window=60.0)
        now = time.monotonic()
        rl._calls = [now - 1, now - 2, now - 3]
        assert rl._allow()

    def test_block_when_exceeded(self) -> None:
        rl = RateLimiter(max_calls=2, window=60.0)
        now = time.monotonic()
        rl._calls = [now - 1, now - 2]
        assert not rl._allow()

    def test_exactly_at_limit(self) -> None:
        rl = RateLimiter(max_calls=3, window=60.0)
        now = time.monotonic()
        rl._calls = [now - 1, now - 2, now - 3]
        assert not rl._allow()

    def test_prune_old_calls(self) -> None:
        rl = RateLimiter(max_calls=2, window=0.001)
        now = time.monotonic()
        rl._calls = [now - 10, now - 10]
        assert rl._allow()

    def test_prune_empty_list(self) -> None:
        rl = RateLimiter(max_calls=5, window=60.0)
        rl._calls = []
        assert rl._allow()

    def test_prune_mixed_calls(self) -> None:
        rl = RateLimiter(max_calls=2, window=0.1)
        now = time.monotonic()
        rl._calls = [now - 10, now - 0.05]
        assert rl._allow()

    def test_allow_zero_window(self) -> None:
        rl = RateLimiter(max_calls=2, window=0.0)
        now = time.monotonic()
        rl._calls = [now]
        assert rl._allow()


class TestDecorator:
    @pytest.mark.asyncio
    async def test_allows_within_limit(self) -> None:
        rl = RateLimiter(max_calls=2, window=60.0)

        @rl
        async def test_func() -> str:
            return "ok"

        assert await test_func() == "ok"

    @pytest.mark.asyncio
    async def test_blocks_when_exceeded(self) -> None:
        rl = RateLimiter(max_calls=1, window=60.0)

        @rl
        async def test_func() -> str:
            return "ok"

        assert await test_func() == "ok"
        with pytest.raises(RuntimeError, match="Rate limit exceeded"):
            await test_func()
