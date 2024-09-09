import os
import secrets

from ddeutil.core import str2bool

env = os.getenv


class BaseConfig:
    API_PREFIX: str = "api/v1/"

    OBSERVE_SQLALCHEMY_DB_ASYNC_URL: str = env(
        "OBSERVE_SQLALCHEMY_DB_ASYNC_URL",
        (
            "sqlite+aiosqlite://{DB_USER}:{DB_PASSWORD}@{DB_HOST}/{DB_NAME}"
        ).format(
            DB_USER=env("OBSERVE_DB_USER", ""),
            DB_PASSWORD=(
                f":{pwd}" if (pwd := env("OBSERVE_DB_PASSWORD")) else ""
            ),
            DB_HOST=env("OBSERVE_DB_HOST", ""),
            DB_NAME=env("OBSERVE_DB_NAME", "observe.db"),
        ),
    )
    OBSERVE_LOG_DEBUG_MODE: bool = str2bool(
        env("OBSERVE_LOG_DEBUG_MODE", "true")
    )

    # NOTE:
    #   token: 30 minutes = 30 minutes
    #   refresh: 60 minutes * 24 hours * 8 days = 8 days
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 8
    OBSERVE_SECRET_KEY: str = env(
        "OBSERVE_CORE_ACCESS_SECRET_KEY", secrets.token_urlsafe(32)
    )
    OBSERVE_REFRESH_SECRET_KEY: str = env(
        "OBSERVE_REFRESH_SECRET_KEY", secrets.token_urlsafe(32)
    )


config = BaseConfig
