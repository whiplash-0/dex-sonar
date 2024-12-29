import asyncio
from typing import Coroutine, Optional


class AsyncInfiniteTasks:
    def __init__(self, *tasks: Coroutine):
        self.tasks: list[asyncio.Task] | list[Coroutine] = tasks
        self.loop: Optional[asyncio.AbstractEventLoop] = None

    async def run(self):
        try:
            self.loop = asyncio.get_event_loop()
            self.tasks = [asyncio.create_task(x) for x in self.tasks]
            await asyncio.gather(*self.tasks)
        except asyncio.CancelledError:
            ...

    def run_coroutine_threadsafe(self, coro: Coroutine):
        asyncio.run_coroutine_threadsafe(coro, self.loop)
