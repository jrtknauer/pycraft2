import asyncio
from typing import Optional

import structlog

from pycraft2.controller import Controller
from pycraft2.log import Logging
from pycraft2.match import Match, MatchResult
from pycraft2.player import Bot
from pycraft2.port import MatchPortConfig

LOGGER = structlog.get_logger(__name__)


class LocalRunner:
    """"""

    def __init__(self, match_configuration: Match) -> None:
        """"""
        Logging.configure_logging()
        self._match_configuration = match_configuration
        self._controllers: list[Controller] = []

    @classmethod
    async def run_local_match(cls, match_configuration: Match) -> None:
        """"""
        runner = cls(match_configuration)
        try:
            await runner._run_local_match()
        except AssertionError as e:
            # Unhandled assertions are likely due to regressions as entering the
            # asserted states means one or more invariants were invalidated.
            LOGGER.critical("Assertion failed", assertion=e)
        except RuntimeError as e:
            # General catch for time being.
            LOGGER.critical("Unrecoverable runtime error.", error=e)
        finally:
            await runner._clean_up_controllers()

    async def _run_local_match(self) -> None:
        """"""
        # Computer players do not require a Controller.
        self._controllers = [
            Controller(player)
            for player in self._match_configuration.players
            if isinstance(player, Bot)
        ]
        multiplayer: bool = True if len(self._controllers) > 1 else False

        # Favor stability over retries with blocking client launches. Recovering from
        # invalid states with multiple StarCraft II clients is complicated, and
        # concurrent launches of StarCraft II on certain platforms increases the
        # likelihood of errors.
        LOGGER.info("Launching required StarCraft II clients.")
        for controller in self._controllers:
            await controller.launch_sc2()

        # After the StarCraft II game clients are running, communication between
        # Controllers and StarCraft II can be concurrent.
        LOGGER.info("Connecting to StarCraft II client API server.")
        await asyncio.gather(
            *(controller.connect() for controller in self._controllers)
        )

        LOGGER.info("StarCraft II host client creating match.")
        # Only one client (the match "host") creates the game with RequestCreateGame.
        await self._controllers[0].create_match(self._match_configuration)

        # Multiplayer ports are only required for a multiplayer match.
        port_configuration: Optional[MatchPortConfig] = None
        if multiplayer:
            port_configuration = MatchPortConfig()

        LOGGER.info("StarCraft II clients joining match.")
        # Have all controllers join the match. If the match is multiplayer, the
        # StarCraft II game clients will synchronize over the multiplayer ports and
        # respond when ready to commence the match.
        await asyncio.gather(
            *(
                controller.join_match(port_configuration)
                for controller in self._controllers
            )
        )

        LOGGER.info("Begin playing the match.")
        # Play match to completion.
        match_result: list[Optional[MatchResult]] = []
        while True:
            match_result: list[Optional[MatchResult]] = await asyncio.gather(
                *(controller.play_match() for controller in self._controllers)
            )

            # Match has ended.
            if None not in match_result:
                LOGGER.info("Match has ended.", results=match_result)
                break

        # Disconnect from the match cleanly - not required for Bot vs AI matches, but
        # to be consistent across implementations perform it anyway.
        LOGGER.info("StarCraft II client(s) leaving the match.")
        await asyncio.gather(
            *(controller.leave_match() for controller in self._controllers)
        )

        # Request StarCraft II to shut down. While Controllers can clean up their own
        # resources, RequestQuitGame will set the API Status to "quit" and prevent any
        # additional actions.
        LOGGER.info("Shutting down StarCraft II client(s).")
        await asyncio.gather(
            *(controller.quit_game() for controller in self._controllers)
        )

    async def _clean_up_controllers(self) -> None:
        """Trigger cleanup for all Controllers."""
        await asyncio.gather(
            *(controller.clean_up() for controller in self._controllers)
        )
