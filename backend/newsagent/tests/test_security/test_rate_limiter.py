import time

import pytest

from newsagent.security.rate_limiter import RateLimiter


class TestAcquire:
    @pytest.mark.asyncio
    async def test_acquire_returns_true_within_limit(self) -> None:
        rl = RateLimiter(max_calls=5, window=60.0, use_redis=False)
        assert await rl.acquire()
        assert len(rl._calls) == 1

    @pytest.mark.asyncio
    async def test_acquire_records_call(self) -> None:
        rl = RateLimiter(max_calls=5, window=60.0, use_redis=False)
        await rl.acquire()
        await rl.acquire()
        await rl.acquire()
        assert len(rl._calls) == 3

    @pytest.mark.asyncio
    async def test_acquire_blocks_when_exceeded(self) -> None:
        rl = RateLimiter(max_calls=2, window=60.0, use_redis=False)
        assert await rl.acquire()
        assert await rl.acquire()
        assert not await rl.acquire()
        assert len(rl._calls) == 2

    @pytest.mark.asyncio
    async def test_acquire_exactly_at_limit(self) -> None:
        rl = RateLimiter(max_calls=3, window=60.0, use_redis=False)
        assert await rl.acquire()
        assert await rl.acquire()
        assert await rl.acquire()
        assert not await rl.acquire()

    @pytest.mark.asyncio
    async def test_acquire_prunes_old_calls(self) -> None:
        rl = RateLimiter(max_calls=2, window=0.001, use_redis=False)
        now = time.monotonic()
        rl._calls = [now - 10, now - 10]
        assert await rl.acquire()
        assert len(rl._calls) == 1

    @pytest.mark.asyncio
    async def test_acquire_zero_window(self) -> None:
        rl = RateLimiter(max_calls=2, window=0.0, use_redis=False)
        assert await rl.acquire()
        assert await rl.acquire()
        assert await rl.acquire()


class TestAllow:
    def test_within_limit(self) -> None:
        rl = RateLimiter(max_calls=5, window=60.0, use_redis=False)
        rl._calls = [1.0, 2.0, 3.0]
        assert rl._allow()

    def test_block_when_exceeded(self) -> None:
        rl = RateLimiter(max_calls=2, window=60.0, use_redis=False)
        rl._calls = [1.0, 2.0]
        assert not rl._allow()

    def test_exactly_at_limit(self) -> None:
        rl = RateLimiter(max_calls=3, window=60.0, use_redis=False)
        rl._calls = [1.0, 2.0, 3.0]
        assert not rl._allow()

    def test_empty_list_allows(self) -> None:
        rl = RateLimiter(max_calls=5, window=60.0, use_redis=False)
        rl._calls = []
        assert rl._allow()

    def test_allow_zero_window(self) -> None:
        rl = RateLimiter(max_calls=2, window=0.0, use_redis=False)
        rl._calls = [1.0]
        assert rl._allow()


class TestPrune:
    def test_prune_old_calls(self) -> None:
        rl = RateLimiter(max_calls=2, window=10.0, use_redis=False)
        now = time.monotonic()
        rl._calls = [now - 20, now - 1]
        rl._prune()
        assert len(rl._calls) == 1

    def test_prune_empty_list(self) -> None:
        rl = RateLimiter(max_calls=5, window=60.0, use_redis=False)
        rl._calls = []
        rl._prune()
        assert len(rl._calls) == 0

    def test_prune_keeps_recent(self) -> None:
        rl = RateLimiter(max_calls=2, window=60.0, use_redis=False)
        now = time.monotonic()
        rl._calls = [now - 10, now - 5]
        rl._prune()
        assert len(rl._calls) == 2


class TestDecorator:
    @pytest.mark.asyncio
    async def test_allows_within_limit(self) -> None:
        rl = RateLimiter(max_calls=2, window=60.0, use_redis=False)

        @rl
        async def test_func() -> str:
            return "ok"

        assert await test_func() == "ok"

    @pytest.mark.asyncio
    async def test_blocks_when_exceeded(self) -> None:
        rl = RateLimiter(max_calls=1, window=60.0, use_redis=False)

        @rl
        async def test_func() -> str:
            return "ok"

        assert await test_func() == "ok"
        with pytest.raises(RuntimeError, match="Rate limit exceeded"):
            await test_func()


class TestRedisRateLimiter:
    @pytest.mark.asyncio
    async def test_redis_acquire_enforces_limits(self) -> None:
        # Instansiasi RateLimiter dengan Redis nyata diaktifkan
        rl = RateLimiter(max_calls=3, window=10.0, use_redis=True)
        await rl._ensure_redis()

        # Lewati tes jika Redis tidak berjalan di port default atau URL tidak diset
        if not rl._redis:
            pytest.skip("Redis server is not available.")

        # Hapus kunci lama agar pengujian selalu segar (pristine state)
        key = "newsagent:rate_limit:global"
        await rl._redis.delete(key)

        # Lakukan 3 panggilan yang valid
        assert await rl.acquire()
        assert await rl.acquire()
        assert await rl.acquire()

        # Panggilan ke-4 harus diblokir karena melebihi max_calls = 3
        assert not await rl.acquire()
