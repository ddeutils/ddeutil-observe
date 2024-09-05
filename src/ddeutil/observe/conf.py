import os
import secrets

from ddeutil.core import str2bool


class BaseConfig:
    API_PREFIX: str = "api/v1/"

    OBSERVE_SQLALCHEMY_DB_ASYNC_URL: str = os.getenv(
        "OBSERVE_SQLALCHEMY_DB_ASYNC_URL",
        (
            "sqlite+aiosqlite://{DB_USER}:{DB_PASSWORD}@{DB_HOST}/{DB_NAME}"
        ).format(
            DB_USER=os.getenv("OBSERVE_DB_USER", ""),
            DB_PASSWORD=(
                f":{pwd}" if (pwd := os.getenv("OBSERVE_DB_PASSWORD")) else ""
            ),
            DB_HOST=os.getenv("OBSERVE_DB_HOST", ""),
            DB_NAME=os.getenv("OBSERVE_DB_NAME", "observe.db"),
        ),
    )
    OBSERVE_LOG_DEBUG_MODE: bool = str2bool(
        os.getenv("OBSERVE_LOG_DEBUG_MODE", "true")
    )

    # NOTE: 60 minutes * 24 hours * 8 days = 8 days
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 8
    OBSERVE_SECRET_KEY: str = os.getenv(
        "OBSERVE_SECRET_KEY", secrets.token_urlsafe(32)
    )


config = BaseConfig
