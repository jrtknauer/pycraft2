"""E2E test setup for a Bot vs AI, Bot vs Bot matches.

The setup is quite crude, but for the interim use a single E2E test file for
docker compose to consume until a more robust framework is established.

"""

import os

from s2clientprotocol.common_pb2 import Race

from pycraft2.bot import BotInterface
from pycraft2.main import run_local_match
from pycraft2.map import Map
from pycraft2.match import Match
from pycraft2.player import CreatePlayer

EXAMPLE_MAPS_DIR = os.path.dirname(os.path.realpath(__file__)) + "/maps"


class _TestBot(BotInterface):
    """"""

    def on_step(self) -> None:
        """"""
        pass


if __name__ == "__main__":
    """Configure the match and run."""
    map_path = Map(EXAMPLE_MAPS_DIR + "/AbyssalReefLE.SC2Map")
    match_configuration = Match(
        map=map_path,
        players=[
            CreatePlayer.bot(Race.Protoss, _TestBot()),
            CreatePlayer.computer(Race.Protoss),
        ],
    )

    run_local_match(match_configuration)

    match_configuration = Match(
        map=map_path,
        players=[
            CreatePlayer.bot(Race.Protoss, _TestBot()),
            CreatePlayer.bot(Race.Terran, _TestBot()),
        ],
    )

    run_local_match(match_configuration)
