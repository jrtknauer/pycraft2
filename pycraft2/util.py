"""Utility classes and functions for pycraft2.

Public functions:
    unused_port_generator

"""

from typing import Any, Generator

import structlog
from portpicker import NoFreePortFoundError, pick_unused_port  # pyright: ignore

LOGGER = structlog.get_logger(__name__)


def unused_port_generator() -> Generator[int, Any, Any]:
    """Reserve and yield an unused port for the current process.

    Returns:
        A unused port as an integer.

    Raises:
        NoFreePortFoundError: portpicker was unable to acquire an unused port.

    """
    while True:
        try:
            port = pick_unused_port()  # pyright: ignore[reportUnknownVariableType]
        except NoFreePortFoundError as e:
            # TODO: custom exception
            LOGGER.error("No unused port available.")
            raise e

        yield port
