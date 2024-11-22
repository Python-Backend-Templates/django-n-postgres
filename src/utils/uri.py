from config import config


def build_absolute_uri(path: str) -> str:
    if not path.startswith("/"):
        path = "/" + path
    return config.ABSOLUTE_URL + path
