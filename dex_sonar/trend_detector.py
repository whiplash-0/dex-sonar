from dataclasses import dataclass
from datetime import datetime
from typing import Callable, Optional

from dex_sonar import time
from dex_sonar.pair import Pair, Turnover
from dex_sonar.time_series import Index


Change = float
Range = int


@dataclass
class Trend:
    change: Change
    start: Index
    end: Index


class TrendDetector:
    def __init__(
            self,
            max_range: Range,
            absolute_change_threshold: Callable[[Range], Change],
            turnover_multiplier: Callable[[Turnover], float] = lambda _: 1,
    ):
        self.max_range = max_range
        self.absolute_change_threshold = absolute_change_threshold
        self.turnover_multiplier = turnover_multiplier
        self.last_detection: dict[Pair, datetime] = {}

    def detect(self, pair: Pair) -> Optional[Trend]:
        prices = pair.prices

        for range_ in range(2, min(self.max_range + 1, len(prices))):
            change = (pair.price - prices[-range_]) / prices[-range_]

            if abs(change) >= self.absolute_change_threshold(range_) * self.turnover_multiplier(pair.turnover):
                self.last_detection[pair] = time.get_timestamp()
                return Trend(
                    change=change,
                    start=prices.get_last_index() - range_ + 1,
                    end=prices.get_last_index(),
                )

        return None

    def get_last_detection_time(self, pair: Pair) -> datetime:
        return self.last_detection.get(pair, time.MIN_TIMESTAMP)
