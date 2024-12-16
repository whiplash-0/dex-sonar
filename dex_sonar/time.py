from datetime import datetime, timedelta, timezone


MIN_TIMESTAMP = datetime.min.replace(tzinfo=timezone.utc)


def get_timestamp() -> datetime:
    return datetime.now(timezone.utc)

def ceil_timestamp_minute(timestamp: datetime) -> datetime:
    ceiled_part = timedelta(seconds=timestamp.second, microseconds=timestamp.microsecond)
    return timestamp if not ceiled_part else timestamp - ceiled_part + timedelta(minutes=1)
