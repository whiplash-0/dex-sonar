from dataclasses import dataclass
from datetime import datetime, timedelta, timezone


MIN_TIMESTAMP = datetime.min.replace(tzinfo=timezone.utc)


def get_timestamp() -> datetime:
    return datetime.now(timezone.utc)


def get_time_passed_since(ts: datetime) -> timedelta:
    return datetime.now(timezone.utc) - ts


def ceil_timestamp_minute(ts: datetime) -> datetime:
    ceiled_part = timedelta(seconds=ts.second, microseconds=ts.microsecond)
    return ts if not ceiled_part else ts - ceiled_part + timedelta(minutes=1)


@dataclass
class _TimeUnit:
    name: str
    short_name: str
    time: timedelta

    def format_units(self, units: int, shorten: bool = False) -> str:
        return f'{units} {self.name if not shorten else self.short_name}{"" if units == 1 else "s"}'

_time_units = [
    _TimeUnit(*x) for x in
    [
        ('second', 'sec', timedelta(seconds=1)),
        ('minute', 'min', timedelta(minutes=1)),
        ('hour', 'hour', timedelta(hours=1)),
        ('day', 'day', timedelta(days=1)),
        ('month', 'month', timedelta(days=30)),
        ('year', 'year', timedelta(days=365)),
    ]
]

def format_timedelta(td: timedelta, shorten: bool = False) -> str:
    for tu in reversed(_time_units):
        if td >= tu.time: return tu.format_units(td // tu.time, shorten)
    return _time_units[0].format_units(0, shorten)
