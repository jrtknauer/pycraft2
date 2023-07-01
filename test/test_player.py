"""Test the pycraft2.player module."""

from typing import Optional

import pytest

from pycraft2.bot import BotInterface
from pycraft2.player import Bot, Computer, CreatePlayer, PlayerClientConfiguration
from pycraft2.s2clientprotocol.common_pb2 import Race
from pycraft2.s2clientprotocol.sc2api_pb2 import AIBuild, Difficulty, PlayerType


class _MockBot(BotInterface):
    """Mock bot implementation."""

    def on_step(self) -> None:
        """Do nothing."""
        pass


def _mock_bot_default(race: Race.ValueType) -> Bot:
    """Fixture for default Bot instantiation."""
    return Bot(
        PlayerType.Participant,
        name=None,
        race=race,
        implementation=_MockBot(),
        client_configuration=PlayerClientConfiguration(),
    )


def _mock_computer_default(race: Optional[Race.ValueType]) -> Computer:
    """Fixuture for a default Computer instantiation with optional race selection."""
    if race is None:
        return Computer(
            PlayerType.Computer,
            name=None,
            race=Race.Random,
            ai_build=AIBuild.RandomBuild,
            ai_difficulty=Difficulty.Medium,
        )
    return Computer(
        PlayerType.Computer,
        name=None,
        race=race,
        ai_build=AIBuild.RandomBuild,
        ai_difficulty=Difficulty.Medium,
    )


class TestCreatePlayer:
    """Test the CreatePlayer class."""

    @pytest.mark.parametrize(
        "race, expected_bot",
        [
            (Race.Random, _mock_bot_default(Race.Random)),
            (
                Race.Protoss,
                _mock_bot_default(Race.Protoss),
            ),
            (
                Race.Terran,
                _mock_bot_default(Race.Terran),
            ),
            (
                Race.Zerg,
                _mock_bot_default(Race.Zerg),
            ),
        ],
    )
    def test_create_player_bot_default(
        self, race: Race.ValueType, expected_bot: Bot
    ) -> None:
        """Test CreatePlayer.bot default interface.

        PlayerClientConfiguration() between different instantiations will not be
        strictly equivalent because a unused port is selected for each instance.

        """
        bot = CreatePlayer.bot(race, _MockBot())
        assert bot == expected_bot

    @pytest.mark.parametrize(
        "race, expected_computer",
        [
            (None, _mock_computer_default(None)),
            (Race.Protoss, _mock_computer_default(Race.Protoss)),
            (Race.Terran, _mock_computer_default(Race.Terran)),
            (Race.Zerg, _mock_computer_default(Race.Zerg)),
        ],
    )
    def test_create_player_computer_default(
        self, race: Optional[Race.ValueType], expected_computer: Computer
    ) -> None:
        """Test CreatePlayer.computer default and race selected interface."""
        if race is None:
            computer = CreatePlayer.computer()
        else:
            computer = CreatePlayer.computer(race)

        assert computer == expected_computer


class TestPlayerClientConfiguration:
    """Test the PlayerClientConfiguration class."""

    def test_config_default(self) -> None:
        """Test the default instantiation."""
        config = PlayerClientConfiguration()
        assert config.sc2_api_address == "127.0.0.1"
        assert isinstance(config.sc2_api_port, int)

        # Verbosity should be false by default
        assert not config.verbose

        # For the remaining fields, only check that the interfaces exist. Leave type
        # validation to the linter.
        assert config.fullscreen is not None
        assert config.window_width is not None
        assert config.window_height is not None
        assert config.window_x is not None
        assert config.window_y is not None
