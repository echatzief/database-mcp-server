import os

def get_required_env(key: str) -> str:
    value = os.environ.get(key)
    if not value:
        raise ValueError(f"Required environment variable '{key}' is not set or empty")
    return value