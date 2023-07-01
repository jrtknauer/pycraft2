"""Example Bot vs AI setup."""

import os

from pycraft2.bot import BotInterface
from pycraft2.main import run_local_match
from pycraft2.map import Map
from pycraft2.match import Match
from pycraft2.player import CreatePlayer
from pycraft2.s2clientprotocol.common_pb2 import Race

EXAMPLE_MAPS_DIR = os.path.dirname(os.path.realpath(__file__)) + "/maps"


class ExampleBot(BotInterface):
    """"""

    def on_step(self) -> None:
        """"""
        pass


if __name__ == "__main__":
    """Configure the match and run."""
    # Use example/maps/AbyssalReefLE.SC2Map
    map_path = Map(EXAMPLE_MAPS_DIR + "/AbyssalReefLE.SC2Map")
    match_configuration = Match(
        map=map_path,
        players=[
            CreatePlayer.bot(Race.Protoss, ExampleBot()),
            CreatePlayer.computer(Race.Protoss),
        ],
    )

    run_local_match(match_configuration)
