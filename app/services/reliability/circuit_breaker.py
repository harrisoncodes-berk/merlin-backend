import time


class CircuitBreaker:
    def __init__(self, open_threshold: int, reset_seconds: int):
        self.open_threshold = open_threshold
        self.reset_seconds = reset_seconds
        self._fail_count = 0
        self._opened_at = 0.0

    def is_open(self) -> bool:
        if self._opened_at == 0:
            return False
        if time.time() - self._opened_at >= self.reset_seconds:
            self._fail_count = 0
            self._opened_at = 0.0
            return False
        return True

    def record_success(self) -> None:
        self._fail_count = 0
        self._opened_at = 0.0

    def record_failure(self) -> None:
        self._fail_count += 1
        if self._fail_count >= self.open_threshold and self._opened_at == 0.0:
            self._opened_at = time.time()

    def remaining_cooldown(self) -> int:
        if not self.is_open():
            return 0
        return max(0, int(self.reset_seconds - (time.time() - self._opened_at)))
