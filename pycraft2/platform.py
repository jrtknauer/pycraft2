"""Interfaces for StarCraft II installation paths on different operating systems.

Public classes:
    System
    Linux
    Windows

"""

from __future__ import annotations

import platform
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import ClassVar, Optional

import structlog

LOGGER = structlog.get_logger(__name__)


class _SupportedSystem(Enum):
    """Enumerations of platform.system()."""

    LINUX = "Linux"
    WINDOWS = "Windows"


@dataclass(slots=True)
class System(ABC):
    """Abstract base class for StarCraft II installation paths.

    Attributes:
        map_dir: Path to the StarCraft II Maps/ directory.
        binary_path: Path to the StarCraft II executable.
        cwd: Path to the directory StarCraft II should execute from.

    """

    _cwd: Optional[Path] = field(init=False)
    _map_dir: Path = field(init=False)
    _binary_path: Path = field(init=False)

    def __post_init__(self) -> None:
        """Use setattr to circumvent frozen=True to init remaining attributes."""
        # Notes regarding Maps/ versus maps/ directory case sensitivity:
        #
        # The StarCraft II API has a "bug" where if StarCraft II is installed at the
        # platform's default directory, the API will not behave as expected. If an
        # absolute path for a map is sent to the API with a default installation, the
        # API has some hard-coded behavior where it mutates the Maps/ directory to
        # /maps in the path.
        #
        # Instead of forcing users to symlink to cover both cases, pycraft2 loads the
        # map data directly to the API to circumvent this issue altogether.
        #
        # For more implementation details, see LocalMapMessage.message().
        self._cwd = self._default_cwd
        self._map_dir = self._default_sc2_path / "Maps"

        # Find the StarCraft II executable.
        executable_versions: Path = self._default_sc2_path / "Versions"
        self._binary_path = (
            next(executable_versions.glob("Base*")) / self._default_sc2_binary
        )

    @property
    @abstractmethod
    def _default_sc2_path(self) -> Path:
        """Each system must specify the default StarCraft II installation directory.

        This is not the directory where the binary is installed, but rather where the
        root folder for the StarCraft II game files are located.
        """
        raise NotImplementedError

    @property
    @abstractmethod
    def _default_sc2_binary(self) -> Path:
        """Each system must specify the SC2 binary to search for."""
        raise NotImplementedError

    @property
    @abstractmethod
    def _default_cwd(self) -> Path:
        """"""
        raise NotImplementedError

    @classmethod
    def detect_system(cls) -> System:
        """Detect and return the System subclass.

        Returns:
            Subclass for the system which pycraft2 is executing under.
        """
        system = platform.system()
        match system:
            case Linux.system:
                return Linux()
            case Windows.system:
                return Windows()
            case _:
                # TODO: While pycraft2 can eventually support all the major platforms,
                # it would be beneficial to provide a custom System interface for users
                # to override the installation, maps, binary, and support directory as
                # needed. This way pycraft2 does not need to explicitly support all
                # systems, but rather empower the users to configure pycraft2 to their
                # own needs.
                raise OSError()

    @property
    def map_dir(self) -> Path:
        """Read-only property for the StarCraft II maps directory."""
        return self._map_dir

    @property
    def binary_path(self) -> Path:
        """Read-only property for the StarCraft II binary path."""
        return self._binary_path

    @property
    def cwd(self) -> Optional[Path]:
        """Read-only property for the StarCraft II execution path."""
        return self._cwd


@dataclass(slots=True)
class Linux(System):
    """StarCraft II default installation paths for Linux."""

    system: ClassVar[str] = _SupportedSystem.LINUX.value
    _default_sc2_binary: ClassVar[  # pyright: ignore[reportIncompatibleMethodOverride]
        Path
    ] = Path("SC2_x64")
    _default_sc2_path: ClassVar[  # pyright: ignore[reportIncompatibleMethodOverride]
        Path
    ] = Path("~/StarCraftII").expanduser()
    _default_cwd: ClassVar[  # pyright: ignore[reportIncompatibleMethodOverride]
        None
    ] = None


@dataclass(slots=True)
class Windows(System):
    """StarCraft II default installation paths for Windows."""

    system: ClassVar[str] = _SupportedSystem.WINDOWS.value
    _default_sc2_binary: ClassVar[  # pyright: ignore[reportIncompatibleMethodOverride]
        Path
    ] = Path("SC2_x64.exe")
    _default_sc2_path: ClassVar[  # pyright: ignore[reportIncompatibleMethodOverride]
        Path
    ] = Path("C:/Program Files (x86)/StarCraft II")
    _default_cwd: ClassVar[  # pyright: ignore[reportIncompatibleMethodOverride]
        Path
    ] = Path("C:/Program Files (x86)/StarCraft II/Support64")
