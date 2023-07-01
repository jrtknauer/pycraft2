"""Entry point functions for running StarCraft II bot matches.

Public functions:
    run_local_match
    join_ladder_match

"""

import argparse
import asyncio
from typing import Optional

from pycraft2.bot import BotInterface
from pycraft2.ladder import LadderArg, LadderRunner
from pycraft2.match import Match
from pycraft2.player import CreatePlayer, PlayerClientConfiguration
from pycraft2.runner import LocalRunner
from pycraft2.s2clientprotocol.common_pb2 import Race


def run_local_match(match_config: Match) -> None:
    """Run a match using a local StarCraft II installation.

    Args:
        match_config: StarCraft II match configuration to run.

    """
    asyncio.get_event_loop().run_until_complete(
        LocalRunner.run_local_match(match_config)
    )


def join_ladder_match(
    race: Race.ValueType, bot_interface: BotInterface, name: Optional[str] = None
) -> None:
    """Join a match managed by the StarCraft II AI Arena ladder manager.

    Args:
        race: StarCraft II race the bot will join the match as.
        bot_interface: Instance of the bot implementation.
        name: Name for the bot to join the match with.

    """
    # Parse ladder CLI to finish configuring for ladder play.
    parser = argparse.ArgumentParser()
    parser.add_argument(LadderArg.API_ADDRESS.value, type=str)
    parser.add_argument(LadderArg.API_PORT.value, type=int)
    parser.add_argument(LadderArg.START_PORT.value, type=int)
    args, _ = parser.parse_known_args()

    bot = CreatePlayer.bot(
        race=race,
        implementation=bot_interface,
        name=name,
        client_configuration=PlayerClientConfiguration(
            sc2_api_address=args.LadderServer, sc2_api_port=args.GamePort
        ),
    )

    asyncio.get_event_loop().run_until_complete(
        LadderRunner.join_match(bot, args.StartPort)
    )
