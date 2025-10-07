import asyncio
from typing import Callable, TypeVar

T = TypeVar("T")


def _is_retryable(exc: Exception) -> bool:
    retryable = ("Timeout" in type(exc).__name__) or ("temporar" in str(exc).lower())
    return retryable


async def with_retries(
    fn,
    *,
    max_retries: int,
    backoff_ms: int,
    on_retry: Callable[[int, Exception], None],
) -> T:
    attempt = 0
    while True:
        try:
            return await fn()
        except Exception as e:
            if attempt >= max_retries or not _is_retryable(e):
                raise
            attempt += 1
            on_retry(attempt, e)
            await asyncio.sleep(backoff_ms / 1000.0)
