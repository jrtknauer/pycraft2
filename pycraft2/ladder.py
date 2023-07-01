"""Command line interface for configuring Pycraft2-based bots.

The CLI is compatible with the AI Arena ladder CLI, so it can be used to package
bots for play on the ladder.

"""
from enum import Enum
from typing import Optional

import structlog

from pycraft2.controller import Controller
from pycraft2.match import MatchResult
from pycraft2.player import Bot
from pycraft2.port import MatchPortConfig

LOGGER = structlog.get_logger(__name__)


class LadderArg(Enum):
    """"""

    API_ADDRESS = "--LadderServer"
    API_PORT = "--GamePort"
    START_PORT = "--StartPort"


class LadderRunner:
    """"""

    def __init__(self, bot: Bot, start_port: int) -> None:
        """"""
        self._bot: Bot = bot
        self._start_port: int = start_port

    @classmethod
    async def join_match(cls, bot: Bot, start_port: int) -> None:
        """"""
        runner = cls(bot, start_port)
        try:
            await runner._join_match()
        except AssertionError:
            pass
        except RuntimeError:
            pass
        finally:
            pass

    async def _join_match(self) -> None:
        """"""
        controller: Controller = Controller(self._bot)
        port_configuration: MatchPortConfig = MatchPortConfig(self._start_port)

        await controller.connect()

        await controller.join_match(port_configuration)

        # Play match to completion.
        match_result: Optional[MatchResult] = None
        while True:
            match_result = await controller.play_match()

            # Match has ended.
            if match_result is not None:
                LOGGER.info("Match has ended.", match_result=match_result)
                break

        # Disconnect from the match before quitting.
        await controller.leave_match()

        # Although the ladder can forcibly cleanup lingering StarCraft II clients,
        # request the client to shut down.
        await controller.quit_game()
