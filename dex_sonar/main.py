import asyncio
import logging
from datetime import timedelta

from dex_sonar import time
from dex_sonar.async_infinite_tasks import AsyncInfiniteTasks
from dex_sonar.bot import Bot
from dex_sonar.config import parameters
from dex_sonar.config.config import config
from dex_sonar.live_pairs import LivePairs
from dex_sonar.logs import setup_logging
from dex_sonar.message import TrendMessage
from dex_sonar.pair import Contract, Pair
from dex_sonar.trend_detector import Trend, TrendDetector


setup_logging()
logger = logging.getLogger(__name__)


class Application:
    def __init__(self):
        self.bot = Bot(
            token=parameters.BOT_TOKEN,
            token_silent=parameters.SILENT_BOT_TOKEN,
        )
        self.pairs = LivePairs(
            update_frequency=config.get_timedelta_from_seconds('Pairs', 'update_frequency'),
            callback_on_update=self.callback_on_pair_update,
            include_filter=lambda pairs: sorted(
                filter(
                    lambda x: x.contract is Contract.USDT,
                    pairs,
                ),
                key=lambda x: x.turnover,
                reverse=True,
            )[:1],
        )
        self.trend_detector = TrendDetector(
            max_range=60,
            absolute_change_threshold=lambda range, is_uptrend: 0.01,
        )
        self.tasks = AsyncInfiniteTasks(
            self.run_loop_updating_status(interval=timedelta(seconds=3)),
            self.run_loop_trend_detection(),
        )
        self.start = time.get_timestamp()
        self.queue = asyncio.Queue()

    def run(self):
        logger.info('Starting bot')
        logger.info('Pairs: ' + ', '.join([x.pretty_symbol for x in self.pairs]))
        asyncio.run(self._run())
        logger.info('Stopping bot')

    async def _run(self):
        await self.bot.run(self.tasks.run())

    async def run_loop_updating_status(self, interval: timedelta):
        try:
            while True:
                await self.update_bot_status()
                await asyncio.sleep(interval.total_seconds())
        finally:
            await self.clear_bot_status()

    async def update_bot_status(self):
        await self.bot.set_description(f'Uptime: {time.format_timedelta(time.get_time_passed_since(self.start), shorten=True)}')

    async def clear_bot_status(self):
        await self.bot.remove_description()

    async def run_loop_trend_detection(self):
        with self.pairs.subscribe_to_stream():
            while True:
                await self.callback_on_pair_update_async_part(*(await self.queue.get()))
                logger.info(f'Callback executed. Queue size: {self.queue.qsize()}')

    def callback_on_pair_update(self, pair: Pair):
        if trend := self.trend_detector.detect(pair):
            logger.info(f'Detected trend in {pair.pretty_symbol}: {trend.change:+.1%}')
            self.tasks.run_coroutine_threadsafe(self.queue.put((pair, trend)))

    async def callback_on_pair_update_async_part(self, pair: Pair, trend: Trend):
        message = TrendMessage(pair, trend)
        await self.bot.send_message(
            parameters.USER_ID,
            message.get_text(),
            message.get_image(),
        )


if __name__ == '__main__':
    Application().run()
