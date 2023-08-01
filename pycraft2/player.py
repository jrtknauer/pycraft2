"""Interfaces to create and configure players for a StarCraft II match.

Public classes:
    Bot
    Computer
    CreatePlayer
    PlayerClientConfiguration

Public type aliases:
    Player

"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Optional, Union

import structlog

# No choice but to use pick_unused_port directly instead of
# pycraft2.util.unused_port_generator because of dataclass limitations for default
# arguments and generators.
from portpicker import pick_unused_port  # pyright: ignore
from s2clientprotocol.common_pb2 import Race
from s2clientprotocol.sc2api_pb2 import AIBuild, Difficulty, PlayerType

from pycraft2.bot import BotInterface

LOGGER = structlog.get_logger(__name__)


# TODO: data_version
# Enables users who have the latest StarCraft II installation to still play on a
# build which properly supports the API.
# https://aiarena.net/wiki/bot-development/#wiki-toc-sc2-version-considerations
@dataclass(frozen=True, slots=True)
class PlayerClientConfiguration:
    """Configuration options for a Player's StarCraft II client.

    Only applicable for _Player subclasses which require a StarCraft II client.

    Attributes:
        sc2_api_address: IPv4 address the StarCraft II API should listen on.
        sc2_api_port: Port the StarCraft II API should listen on.
        fullscreen: Display the StarCraft II client in fullscreen or a window.
        window_width: Width resolution of the StarCraft II client in pixels.
        window_height: Height resolution of the StarCraft II client in pixels.
        verbose: Launch StarCraft II with verbose console output.

    """

    class _Address(Enum):
        """Enumerated listening addresses for the StarCraft II API.

        Attributes:
            LOCALHOST: IPv4 localhost.

        """

        LOCALHOST = "127.0.0.1"

    sc2_api_address: str = _Address.LOCALHOST.value
    sc2_api_port: int = field(default_factory=pick_unused_port)  # pyright: ignore
    fullscreen: bool = False
    window_width: int = 1280
    window_height: int = 720
    window_x: int = 0
    window_y: int = 0
    verbose: bool = False

    def __eq__(self, other: object) -> bool:
        """Override to not compare sc2_api_port.

        Ports are guaranteed by portpicker to be unique, but users should still be able
        to compare if the rest of the configuration is equal to another.

        """
        if not isinstance(other, PlayerClientConfiguration):
            return False

        return (
            self.sc2_api_address == other.sc2_api_address
            and self.fullscreen == other.fullscreen
            and self.window_width == other.window_width
            and self.window_height == other.window_height
            and self.window_x == other.window_x
            and self.window_y == other.window_y
            and self.verbose == other.verbose
        )


@dataclass(frozen=True, slots=True)
class _Player:
    """Shared configuration for StarCraft II players.

    Attributes:
        type: StarCraft II API enumeration for the player type.
        name: Optional in-game name for the player. If no name is provided, the API
            will generate a name.

    """

    type: PlayerType.ValueType
    name: Optional[str]


class CreatePlayer:
    """Interface for creating _Player subclasses."""

    @classmethod
    def bot(
        cls,
        race: Race.ValueType,
        implementation: BotInterface,
        name: Optional[str] = None,
        client_configuration: Optional[PlayerClientConfiguration] = None,
    ) -> Bot:
        """Instantiate and return a Bot instance.

        Args:
            race: StarCraft II race for the bot to play.
            implementation: Instance of the bot implementation.
            name: Player name for the bot to join the match with.
            client_configuration: Configuration options for the StarCraft II client.

        Returns:
            Configured Bot instance.

        """
        # Function argument defaults are evaluated once, and Bots should have distinct
        # configuration objects (otherwise for multiplayer matches the same port will
        # be re-used).
        if client_configuration is None:
            client_configuration = PlayerClientConfiguration()

        return Bot(
            type=PlayerType.Participant,
            name=name,
            race=race,
            implementation=implementation,
            client_configuration=client_configuration,
        )

    @classmethod
    def computer(
        cls,
        race: Race.ValueType = Race.Random,
        ai_build: AIBuild.ValueType = AIBuild.RandomBuild,
        ai_difficulty: Difficulty.ValueType = Difficulty.Medium,
        name: Optional[str] = None,
    ) -> Computer:
        """Instantiate and return a Computer instance.

        Args:
            race: StarCraft II race for the computer to play.
            ai_build: StarCraft II build-order strategy for the computer to use.
            ai_difficulty: Difficulty setting for the computer.
            name: Player name for the computer to join the match with.

        """
        return Computer(
            PlayerType.Computer,
            name=name,
            race=race,
            ai_build=ai_build,
            ai_difficulty=ai_difficulty,
        )


@dataclass(frozen=True, slots=True)
class Bot(_Player):
    """Player configuration for a scripted StarCraft II bot.

    Attributes:
        race: StarCraft II API enumeration for the player race.
        implementation: Instance of the Bot implementation.
        client_configuration: Configuration for the player's client.

    Prefer to instantiate a Bot instance from CreatePlayer.bot().

    """

    race: Race.ValueType
    implementation: BotInterface
    client_configuration: PlayerClientConfiguration


@dataclass(frozen=True, slots=True)
class Computer(_Player):
    """Player configuration for the built-in StarCraft II AI.

    Attributes:
        race:
        ai_build:
        ai_difficulty:

    Prefer to instantiate a Computer instance from CreatePlayer.computer().

    """

    race: Race.ValueType
    ai_build: AIBuild.ValueType
    ai_difficulty: Difficulty.ValueType


Player = Union[Bot, Computer]
"""Union type alias for subclasses of _Player.

Use a type alias so to not export the private _Player base class outside the module,
even for type hints.

"""
