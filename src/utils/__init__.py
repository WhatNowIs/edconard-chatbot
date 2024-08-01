from datetime import datetime


def datetime_to_str(dt):
    if isinstance(dt, datetime):
        return dt.isoformat()
    raise TypeError(f"Object of type {type(dt).__name__} is not JSON serializable")