from datetime import UTC, datetime


def epoch_ms(dt: datetime) -> int:
    return int(dt.timestamp() * 1000)


def datetime_from_ms(ms: int) -> datetime:
    return datetime.fromtimestamp(ms / 1000, tz=UTC)
