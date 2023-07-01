"""StarCraft II map interfaces.

Public classes:
    Map

"""

from dataclasses import InitVar, dataclass, field
from pathlib import Path


@dataclass(slots=True)
class Map:
    """StarCraft II map data.

    InitVars:
        map: The absolute path for the map.

    Attributes:
        path: Path instance for the map path.

    """

    map: InitVar[str]
    path: Path = field(init=False)

    def __post_init__(self, map: str) -> None:
        """Initialize from InitVars."""
        self.path = Path(map)

    @property
    def data(self) -> bytes:
        """Return the binary data for the SC2Map file."""
        with open(self.path, "rb") as f:
            return f.read()
