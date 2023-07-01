"""pycraft2 logging configuration.

Public functions:
    configure_logging

"""

import logging.config
import sys
from dataclasses import dataclass
from typing import Any, ClassVar

import structlog


@dataclass(frozen=True, slots=True)
class Logging:
    """Logging configuration for pycraft2.

    As pycraft2 is still in development, the current configuration does not discard
    DEBUG level logs. As pycraft2 nears a production-ready release, benchmarks will
    be performed to assess the performance overhead of the DEBUG logs and provide an
    interface to configure logging to discard them.

    Attributes:
        _dict_config: Python logging configuration.

    """

    _dict_config: ClassVar[dict[str, Any]] = {
        "version": 1,
        "disable_existing_loggers": False,
        "handlers": {
            # Only log INFO and above events to the console.
            "console": {"class": "logging.StreamHandler", "level": "INFO"},
            "pycraft2_debug_file": {
                "class": "logging.FileHandler",
                "level": "DEBUG",
                "filename": "pycraft2.debug.log",
            },
        },
        "loggers": {
            "pycraft2": {
                "handlers": ["console", "pycraft2_debug_file"],
                "level": "DEBUG",
                "propagate": True,
            },
            # Register the aiohttp.websocket logger, but not much to rely on here.
            # aiohttp does not log any requests or responses, so pycraft will need
            # to do it.
            "aiohttp.websocket": {
                "handlers": ["console"],
                "level": "DEBUG",
                "propagate": True,
            },
        },
    }

    @classmethod
    def configure_logging(cls) -> None:
        """Configure Python logging and output format with structlog."""
        logging.config.dictConfig(cls._dict_config)

        # Recommended structlog configuration.
        # https://www.structlog.org/en/stable/standard-library.html#suggested-configurations
        structlog_processors = [
            # If log level is too low, abort pipeline and throw away log entry.
            structlog.stdlib.filter_by_level,
            # Add the name of the logger to event dict.
            structlog.stdlib.add_logger_name,
            # Add log level to event dict.
            structlog.stdlib.add_log_level,
            # Perform %-style formatting.
            structlog.stdlib.PositionalArgumentsFormatter(),
            # Add a timestamp in ISO 8601 format.
            structlog.processors.TimeStamper(fmt="iso", utc=True),
            # If the "stack_info" key in the event dict is true, remove it and
            # render the current stack trace in the "stack" key.
            structlog.processors.StackInfoRenderer(),
            # If the "exc_info" key in the event dict is either true or a
            # sys.exc_info() tuple, remove "exc_info" and render the exception
            # with traceback into the "exception" key.
            structlog.processors.format_exc_info,
            # If some value is in bytes, decode it to a unicode str.
            # structlog.processors.UnicodeDecoder(),
            # Add callsite parameters.
            structlog.processors.CallsiteParameterAdder(
                {
                    structlog.processors.CallsiteParameter.FILENAME,
                    structlog.processors.CallsiteParameter.FUNC_NAME,
                    structlog.processors.CallsiteParameter.LINENO,
                }
            ),
        ]

        # Use pretty printing when running in a terminal session.
        if sys.stderr.isatty():
            structlog_processors += [structlog.dev.ConsoleRenderer()]
        # Emit JSON with structured tracebacks when running in a container.
        else:
            structlog_processors += [
                structlog.processors.JSONRenderer(),
            ]

        structlog.configure(
            processors=structlog_processors,
            # `wrapper_class` is the bound logger that you get back from
            # get_logger(). This one imitates the API of `logging.Logger`.
            # wrapper_class=structlog.make_filtering_bound_logger(logging.INFO),
            wrapper_class=structlog.stdlib.BoundLogger,
            # `logger_factory` is used to create wrapped loggers that are used for
            # OUTPUT. This one returns a `logging.Logger`. The final value (a JSON
            # string) from the final processor (`JSONRenderer`) will be passed to
            # the method of the same name as that you've called on the bound logger.
            logger_factory=structlog.stdlib.LoggerFactory(),
            # Effectively freeze configuration after creating the first bound
            # logger.
            cache_logger_on_first_use=True,
        )
