# ------------------------------------------------------------------------------
# Copyright (c) 2022 Korawich Anuttra. All rights reserved.
# Licensed under the MIT License. See LICENSE in the project root for
# license information.
# ------------------------------------------------------------------------------
from __future__ import annotations

import logging
import os
from functools import lru_cache

from ddeutil.core import str2bool


@lru_cache
def get_logger(name: str):
    """Return logger with an input module name."""
    logger = logging.getLogger(name)
    formatter = logging.Formatter(
        fmt=(
            "%(asctime)s.%(msecs)03d (%(name)-10s, %(process)-5d, "
            "%(thread)-5d) [%(levelname)-7s] %(message)-120s "
            "(%(filename)s:%(lineno)s)"
        ),
        datefmt="%Y-%m-%d %H:%M:%S",
    )
    stream = logging.StreamHandler()
    stream.setFormatter(formatter)
    logger.addHandler(stream)

    debug: bool = str2bool(os.getenv("OBSERVE_LOG_DEBUG_MODE", "true"))
    logger.setLevel(logging.DEBUG if debug else logging.INFO)
    return logger
