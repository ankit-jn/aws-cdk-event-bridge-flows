from datetime import datetime, timezone

def get_current_timestamp_string() -> str:
    """
    Getting current timestamp
    """
    return str(datetime.now(timezone.utc))