import asyncio
import logging
from typing import Coroutine, Optional


logger = logging.getLogger(__name__)


class AsyncInfiniteTasks:
    def __init__(self, *tasks: Coroutine):
        self.tasks: list[asyncio.Task] | list[Coroutine] = tasks
        self.loop: Optional[asyncio.AbstractEventLoop] = None
        self._are_cancelled = False

    async def run(self):
        try:
            self.loop = asyncio.get_event_loop()
            self.tasks = [asyncio.create_task(x) for x in self.tasks]
            await asyncio.gather(*self.tasks)

        except asyncio.CancelledError:
            logger.debug('Caught `CancelledError`. Cancelling all tasks and waiting for them to complete')
            await self.cancel_all()

    async def cancel_all(self):
        self._are_cancelled = True

        for x in self.tasks:
            if not x.done(): x.cancel()

        await asyncio.gather(*self.tasks, return_exceptions=True)  # supress raising exception, instead handle on task level

    def are_cancelled(self):
        return self._are_cancelled

    def run_coroutine_threadsafe(self, coro: Coroutine):
        asyncio.run_coroutine_threadsafe(coro, self.loop)
