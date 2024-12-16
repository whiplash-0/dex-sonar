from dataclasses import dataclass
from datetime import datetime
from typing import Optional

from dex_sonar.time_series import TimeSeries


Symbol = str


@dataclass
class Pair:
    symbol: Symbol
    prices: TimeSeries[float]
    turnovers: TimeSeries[float]
    turnover: float
    open_interest: float
    funding_rate: Optional[float]
    next_funding_time: datetime

    def update(self, turnover, open_interest, funding_rate, next_funding_time):
        self.turnover = turnover
        self.open_interest = open_interest
        self.funding_rate = funding_rate
        self.next_funding_time = next_funding_time
