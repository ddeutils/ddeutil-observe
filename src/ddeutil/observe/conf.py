# ------------------------------------------------------------------------------
# Copyright (c) 2022 Korawich Anuttra. All rights reserved.
# Licensed under the MIT License. See LICENSE in the project root for
# license information.
# ------------------------------------------------------------------------------
from __future__ import annotations

import os
import secrets

from ddeutil.core import str2bool
from dotenv import load_dotenv

# NOTE: Loading environment variable before initialize the FastApi application.
load_dotenv()

env = os.getenv


class BaseConfig:
    """Base configuration that use on this application on all module that want
    to dynamic value with environment variable changing action.
    """

    API_PREFIX: str = "/api/v1"

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
    LOG_DEBUG_MODE: bool = str2bool(env("OBSERVE_LOG_DEBUG_MODE", "true"))
    LOG_SQLALCHEMY_DEBUG_MODE: bool = str2bool(
        env("OBSERVE_LOG_SQLALCHEMY_DEBUG_MODE", "false")
    )

    # NOTE:
    #   * token:    30 minutes                      = 30 minutes
    #   * refresh:  60 minutes * 24 hours * 8 days  = 8 days
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 8

    # NOTE: Secret keys that use to hash any jwt token generated value.
    SECRET_KEY: str = env(
        "OBSERVE_CORE_ACCESS_SECRET_KEY", secrets.token_urlsafe(32)
    )
    REFRESH_SECRET_KEY: str = env(
        "OBSERVE_REFRESH_SECRET_KEY", secrets.token_urlsafe(32)
    )

    WEB_ADMIN_USER: str = env("OBSERVE_WEB_ADMIN_USER", "observe")
    WEB_ADMIN_PASS: str = env("OBSERVE_WEB_ADMIN_PASS", "observe")
    WEB_ADMIN_EMAIL: str = env("OBSERVE_WEB_ADMIN_EMAIL", "observe@mail.com")


# NOTE: Start initialize base config object.
config = BaseConfig()
