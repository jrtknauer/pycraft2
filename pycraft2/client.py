"""Interfaces to launch and manage a StarCraft II subprocess.

Public classes:
    GameClient

"""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import InitVar, dataclass, field
from enum import Enum
from itertools import chain
from subprocess import Popen
from time import sleep
from typing import ClassVar, Optional

import structlog

from pycraft2.platform import System
from pycraft2.player import PlayerClientConfiguration

LOGGER = structlog.get_logger(__name__)


@dataclass(slots=True)
class GameClient:
    """Launch and terminate a StarCraft II game client subprocess.

    Attributes:
        _system: OS wrapper for the StarCraft II installation.
        _args: CLI arguments to launch StarCraft II with.
        _process: Subprocess handle for the StarCraft II client.
        _wait_for_sc2: Number of seconds to wait after launching a StarCraft II game
            client.

    """

    client_config: InitVar[PlayerClientConfiguration]
    _system: System = field(init=False)
    _args: list[str] = field(init=False)
    _process: Optional[Popen[bytes]] = field(init=False)
    _wait_for_sc2: ClassVar[int] = 2

    def __post_init__(self, client_config: PlayerClientConfiguration) -> None:
        """Init remaining attributes."""
        self._system: System = System.detect_system()
        self._args: list[str] = [
            str(self._system.binary_path)
        ] + _ClientArgumentBuilder(client_config).args()
        self._process: Optional[Popen[bytes]] = None

    def launch(self) -> None:
        """Launches an instance of the StarCraft II game client with CLI arguments.

        Raises:
            FileNotFoundError: StarCraft II executable does not exist.
            RuntimeException: TODO: custom exceptions.

        """
        if self._process is not None:
            # launch has already been called, GameClient is dirty.
            # TODO: custom exception.
            raise RuntimeError

        LOGGER.debug("Launching StarCraft II subprocess.", args=self._args)

        try:
            # For some platforms, the StarCraft II executable must be invoked from the
            # Support64 directory of the installation.
            self._process = Popen(self._args, cwd=self._system.cwd)

            # StarCraft II startup is composed of multiple phases. "Phase 3" is when
            # the API begins listening for connections on the websocket. Ideally we
            # would wait for the console log to report Startup Phase 3, but not all
            # platforms output the same message formats. Instead, wait two seconds for
            # the game client to startup before hammering the websocket with attempted
            # connections.
            sleep(self._wait_for_sc2)
        except FileNotFoundError as e:
            # Handle FileNotFoundError first as it inherits from OSError.
            # SC2 executable not found.
            LOGGER.critical(
                "StarCraft II executable not found.", path=self._system.binary_path
            )
            raise RuntimeError(e)
        except OSError as e:
            # Other unhandled OS errors
            raise RuntimeError(e)
        except ValueError as e:
            # Popen called with invalid arguments
            raise RuntimeError(e)

    def terminate(self) -> None:
        """Terminates the launched instance of the game client."""
        if self._process is not None:
            LOGGER.debug(
                "Terminating StarCraft II subprocess.", subprocess=self._process
            )
            self._process.terminate()


@dataclass(frozen=True, slots=True)
class _ClientArg(ABC):
    """Base class template for an SC2 client argument.

    Attributes:
        value: CLI argument value
        arg: CLI argument

    """

    value: str

    @property
    @abstractmethod
    def arg(self) -> _SC2Arg:
        raise NotImplementedError


class _SC2Arg(Enum):
    """Enumeration of valid StarCraft II launcher arguments."""

    ADDRESS = "-listen"
    PORT = "-port"
    FULLSCREEN = "-displayMode"
    WINDOW_WIDTH = "-windowwidth"
    WINDOW_HEIGHT = "-windowheight"
    WINDOW_X = "-windowx"
    WINDOW_Y = "-windowy"


class _SC2Flag(Enum):
    """Enumeration of valid StarCraft II launcher flags."""

    VERBOSE = "-verbose"


@dataclass(frozen=True, slots=True)
class _ClientFlag:
    """Base class template for a StarCraft II executable flag."""

    flag: ClassVar[_SC2Flag]


@dataclass(frozen=True, slots=True)
class _Verbose(_ClientFlag):
    """Strong type for the -verbose SC2 argument."""

    flag: ClassVar[_SC2Flag] = _SC2Flag.VERBOSE


@dataclass(frozen=True, slots=True)
class _Sc2ApiAddress(_ClientArg):
    """Strong type for the -listen SC2 argument."""

    arg: ClassVar[  # pyright: ignore[reportIncompatibleMethodOverride]
        _SC2Arg
    ] = _SC2Arg.ADDRESS


@dataclass(frozen=True, slots=True)
class _Sc2ApiPort(_ClientArg):
    """Strong type for the -port SC2 argument."""

    arg: ClassVar[  # pyright: ignore[reportIncompatibleMethodOverride]
        _SC2Arg
    ] = _SC2Arg.PORT


@dataclass(frozen=True, slots=True)
class _Fullscreen(_ClientArg):
    """"""

    arg: ClassVar[  # pyright: ignore[reportIncompatibleMethodOverride]
        _SC2Arg
    ] = _SC2Arg.FULLSCREEN


@dataclass(frozen=True, slots=True)
class _WindowWidth(_ClientArg):
    """Strong type for the -windowwidth SC2 argument."""

    arg: ClassVar[  # pyright: ignore[reportIncompatibleMethodOverride]
        _SC2Arg
    ] = _SC2Arg.WINDOW_WIDTH


@dataclass(frozen=True, slots=True)
class _WindowHeight(_ClientArg):
    """Strong type for the -windowheight SC2 argument."""

    arg: ClassVar[  # pyright: ignore[reportIncompatibleMethodOverride]
        _SC2Arg
    ] = _SC2Arg.WINDOW_HEIGHT


@dataclass(frozen=True, slots=True)
class _WindowX(_ClientArg):
    """Strong type for the -windowx StarCraft II argument."""

    arg: ClassVar[  # pyright: ignore[reportIncompatibleMethodOverride]
        _SC2Arg
    ] = _SC2Arg.WINDOW_X


@dataclass(frozen=True, slots=True)
class _WindowY(_ClientArg):
    """Strong type for the -windowy StarCraft II argument."""

    arg: ClassVar[  # pyright: ignore[reportIncompatibleMethodOverride]
        _SC2Arg
    ] = _SC2Arg.WINDOW_Y


class _ClientArgumentBuilder:
    """Constructs StarCraft II CLI arguments from user configuration."""

    def __init__(self, client_configuration: PlayerClientConfiguration) -> None:
        """Translate configuration options to StarCraft II CLI arguments.

        Attributes:
            _args: list of CLI arguments.
            _verbose: boolean to enable or disable the CLI verbose option.

        """
        self._args: list[_ClientArg] = [
            _Sc2ApiAddress(client_configuration.sc2_api_address),
            _Sc2ApiPort(str(client_configuration.sc2_api_port)),
            _Fullscreen(str(0) if not client_configuration.fullscreen else str(1)),
            _WindowWidth(str(client_configuration.window_width)),
            _WindowHeight(str(client_configuration.window_height)),
            _WindowX(str(client_configuration.window_x)),
            _WindowY(str(client_configuration.window_y)),
        ]
        self._verbose: bool = client_configuration.verbose

    def args(self) -> list[str]:
        """Return the client config as subprocess arguments.

        Returns:
            An ordered list of StarCraft II CLI argument strings to be consumed by
            subprocess.Popen.

        """
        # Zipper merge
        args: list[str] = list(
            chain(
                *zip(
                    [client_arg.arg.value for client_arg in self._args],
                    [client_arg.value for client_arg in self._args],
                )
            )
        )

        # Append enabled flags.
        if self._verbose:
            args.append(_Verbose().flag.value)

        return args
