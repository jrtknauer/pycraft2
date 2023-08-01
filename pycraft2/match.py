"""StarCraft II match interfaces.

Public classes:
    Match
    MatchResult

"""
from dataclasses import dataclass

from s2clientprotocol.sc2api_pb2 import Result

from pycraft2.map import Map
from pycraft2.player import Player


@dataclass(frozen=True, slots=True)
class Match:
    """Configuration interface for a StarCraft II match.

    Attributes:
        map: The map to play the match on.
        players: A list of players to play the match with.

    """

    map: Map
    players: list[Player]


@dataclass(frozen=True, slots=True)
class MatchResult:
    """Player results for a StarCraft II match.

    Attributes:
        player_id: StarCraft II API-assigned player ID
        result: The StarCraft II API-enumerated result.
    """

    player_id: int
    result: Result.ValueType
