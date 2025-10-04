import asyncio
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Dict, Tuple, Optional

Key = Tuple[str, str]


@dataclass
class Job:
    task: asyncio.Task
    client_message_id: Optional[str]
    started_at: datetime


class JobRegistry:
    def __init__(self) -> None:
        self._jobs: Dict[Key, Job] = {}
        self._lock = asyncio.Lock()

    async def try_register(
        self, key: Key, task: asyncio.Task, client_message_id: Optional[str]
    ) -> bool:
        async with self._lock:
            if key in self._jobs:
                return False
            self._jobs[key] = Job(
                task=task,
                client_message_id=client_message_id,
                started_at=datetime.now(timezone.utc),
            )
            return True

    async def finish(self, key: Key) -> None:
        async with self._lock:
            self._jobs.pop(key, None)

    async def cancel(self, key: Key) -> bool:
        async with self._lock:
            job = self._jobs.get(key)
            if not job:
                return False
            job.task.cancel()
            return True

    async def has(self, key: Key) -> bool:
        async with self._lock:
            return key in self._jobs


job_registry = JobRegistry()
