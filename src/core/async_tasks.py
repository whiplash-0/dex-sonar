import asyncio
import logging
import signal
import time as pytime
from abc import ABC
from asyncio import AbstractEventLoop, Task as GeneralAsyncioTask
from typing import Any, Callable, Coroutine, Generator, Iterator, Optional

from src.utils.time import Timedelta


logger = logging.getLogger(__name__)


Task = Coroutine[Any, Any, None]
RawTask = Callable[[], Task]
AsyncioTask = GeneralAsyncioTask[None]
TerminationSignalHandler = Callable[[], None]



class AsyncioRunner:
    event_loop: Optional[AbstractEventLoop] = None
    termination_signal_handler: Optional[TerminationSignalHandler] = None
    
    @classmethod
    def init(cls, termination_signal_handler: Optional[TerminationSignalHandler] = None):
        cls.termination_signal_handler: Optional[TerminationSignalHandler] = termination_signal_handler

    @classmethod
    def run(cls, task: Task):
        async def wrap():
            cls.event_loop = asyncio.get_running_loop()

            if cls.termination_signal_handler:
                cls.event_loop.add_signal_handler(signal.SIGINT, cls.termination_signal_handler)
                cls.event_loop.add_signal_handler(signal.SIGTERM, cls.termination_signal_handler)

            return await task

        asyncio.run(wrap())
    
    @classmethod
    def schedule(cls, task: Task):
        """
        Schedules a task for execution, but doesn't necessarily execute it immediately
        """
        asyncio.run_coroutine_threadsafe(task, loop=cls.event_loop)



class AsyncTasksBase(ABC):
    def __init__(self, *tasks: Task):
        self.pending_tasks: Iterator[Task] = iter(tasks)
        self.started_tasks: list[AsyncioTask] = []
        self._are_cancelled = False

    async def stop(self):
        self._are_cancelled = True

        for x in self.pending_tasks:  # ensure there are no non-awaited coroutine objects to avoid runtime warning
            x.close()

        for x in self.started_tasks:
            if not x.done(): x.cancel()

        await asyncio.gather(
            *self.started_tasks,
            return_exceptions=True,  # supress raising exception, instead just keep it in task metadata
        )

    def are_cancelled(self):
        return self._are_cancelled

    def _start(self) -> Generator[AsyncioTask, None, None]:
        for x in self.pending_tasks:
            self.started_tasks.append(asyncio.create_task(x))
            yield self.started_tasks[-1]



class AsyncSequentialTasks(AsyncTasksBase):
    async def run(self):
        try:
            for x in self._start(): await x

        except asyncio.CancelledError:
            logger.debug('Tasks or some task were cancelled. Skipping all following')

        finally:
            await self.stop()



class AsyncConcurrentTasks(AsyncTasksBase):
    """
    In the case of non-blocking run, exceptions should be handled at the individual task level.
    If an exception occurs, all other related tasks should be cancelled accordingly, this won't be done automatically
    """
    async def run(self, blocking=False):
        try:
            started_tasks = [x for x in self._start()]
            if blocking: await asyncio.gather(*started_tasks)

        except asyncio.CancelledError:
            logger.debug('Tasks or some task were cancelled. Cancelling remaining tasks and waiting for them to complete')

        finally:
            if blocking: await self.stop()



class AsyncConcurrentPollingTasks(AsyncConcurrentTasks):
    def __init__(self, *raw_tasks_and_poll_intervals: tuple[RawTask, Timedelta]):
        super().__init__(
            *[self._wrap_task_with_polling(x, y) for x, y in raw_tasks_and_poll_intervals]
        )

    @staticmethod
    async def _wrap_task_with_polling(raw_task, poll_interval):
        while True:
            start = pytime.monotonic()
            await raw_task()
            await asyncio.sleep(max(poll_interval.total_seconds() - (pytime.monotonic() - start), 0))
