from dataclasses import dataclass
from datetime import datetime, timedelta
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
    is_weak: bool

    @property
    def is_normal(self):
        return not self.is_weak


class TrendDetector:
    def __init__(
            self,
            max_range: Range,
            absolute_change_threshold: Callable[[Range], Change],
            turnover_multiplier: Callable[[Turnover], float] = lambda _: 1,
            weak_trend_threshold: Change = 1,
            cooldown: timedelta = timedelta(),
    ):
        self.max_range = max_range
        self.absolute_change_threshold = absolute_change_threshold
        self.turnover_multiplier = turnover_multiplier
        self.weak_trend_threshold = weak_trend_threshold
        self.cooldown = cooldown
        self.last_detection: dict[(Pair, bool), datetime] = {}

    def detect(self, pair: Pair) -> Optional[Trend]:
        if self._is_in_cooldown(pair):
            return None

        prices = pair.prices

        for range_ in range(2, min(self.max_range + 1, len(prices))):
            change = (pair.price - prices[-range_]) / prices[-range_]
            change_threshold = self.absolute_change_threshold(range_) * self.turnover_multiplier(pair.turnover)

            if abs(change) >= change_threshold * self.weak_trend_threshold:
                is_weak = abs(change) < change_threshold

                if is_weak and self._is_in_cooldown(pair, is_weak=is_weak):
                    continue

                self.last_detection[pair, is_weak] = time.get_timestamp()
                return Trend(
                    change=change,
                    start=prices.get_last_index() - range_ + 1,
                    end=prices.get_last_index(),
                    is_weak=is_weak,
                )

        return None

    def _is_in_cooldown(self, pair: Pair, is_weak=False):
        last_detection_time = self.last_detection.get((pair, is_weak), time.MIN_TIMESTAMP)
        return time.get_time_passed_since(last_detection_time) <= self.cooldown
