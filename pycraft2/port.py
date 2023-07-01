"""StarCraft II API multiplayer port configuration interfaces.

The StarCraft II API supports multiplayer Bot versus Bot matches, which requires an
additional four ports (two ports for each client) for clients to communicate over. The
pycraft2.port module implements classes to select the ports required for a multiplayer
match and expose them for usage by the API.

Public classes:
    MatchPortConfig

"""

from __future__ import annotations

from dataclasses import InitVar, dataclass, field
from typing import Optional

from pycraft2.util import unused_port_generator


@dataclass(frozen=True, slots=True)
class PortSet:
    """Strong type for the API port requirements."""

    game_port: int
    base_port: int


@dataclass(slots=True)
class MatchPortConfig:
    """Manage the required port configuration for multiplayer matches.

    Matches which only require a single client (e.g. Bot vs AI(s)) can omit
    configuration of the multiplayer ports. For multiplayer matches, the API requires
    a total of four ports:
        - Two for the game host.
        - Two for the joining client.

    Both the host and the client must communicate all four ports to the API when
    requesting to join the game. For reference, the RequestJoinGame protocol buffer
    schema:
    https://github.com/Blizzard/s2client-proto/blob/master/s2clientprotocol/sc2api.proto#L210

    """

    start_port: InitVar[Optional[int]] = None
    _host_ports: PortSet = field(init=False)
    _client_ports: list[PortSet] = field(init=False)

    def __post_init__(self, start_port: Optional[int]) -> None:
        """Initialize ports.

        Client ports are presented as a list of ports as the StarCraft II API was
        designed to eventually support multiplayer play beyond one-versus-one. However,
        this support was never implemented.

        Although this support is never going to come, the client ports are a repeated
        field in the protocol buffer schema and would need to be passed as a list -
        even if there is only one PortSet to send.

        """
        if start_port is not None:
            self._host_ports = PortSet(start_port + 2, start_port + 3)
            self._client_ports = [PortSet(start_port + 4, start_port + 5)]
        else:
            self._host_ports = PortSet(
                game_port=next(unused_port_generator()),
                base_port=next(unused_port_generator()),
            )
            self._client_ports = [
                PortSet(
                    game_port=next(unused_port_generator()),
                    base_port=next(unused_port_generator()),
                )
            ]

    @property
    def host_ports(self) -> PortSet:
        return self._host_ports

    @property
    def client_ports(self) -> list[PortSet]:
        return self._client_ports
