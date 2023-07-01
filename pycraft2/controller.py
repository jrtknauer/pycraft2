"""Interfaces for StarCraft II client and API lifecycle interactions.

The Controller class implements the StarCraft II API state machine for a single
player.

Public classes:
    Controller

"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Optional

import structlog

from pycraft2.client import GameClient
from pycraft2.match import Match, MatchResult
from pycraft2.message import ResponseMessage
from pycraft2.player import Bot
from pycraft2.port import MatchPortConfig
from pycraft2.s2clientprotocol.sc2api_pb2 import (
    PlayerResult,
    ResponseObservation,
    Status,
)
from pycraft2.transport import Messenger

LOGGER = structlog.get_logger(__name__)


@dataclass(slots=True)
class Controller:
    """Perform StarCraft II client and API lifecycle interactions.

    Attributes:
        _player: Bot instance to play the match for the Controller.
        _client: Client interface to play the match with.
        _messenger: Messenger interface to communicate with the StarCraft II API.
        _player_id: Player ID assigned to _player from the StarCraft II API.
        _server_status: Last updated status of the StarCraft II API.

    Instantiates both the StarCraft II game client and websocket communication
    interfaces to provide a public interface which implements the sc2client-proto state
    machine:
    https://github.com/Blizzard/s2client-proto/blob/master/docs/protocol.md#state-machine

    Server status codes:
    https://github.com/Blizzard/s2client-proto/blob/master/s2clientprotocol/sc2api.proto#L157

    """

    _player: Bot
    _client: GameClient = field(init=False)
    _messenger: Messenger = field(init=False)
    _player_id: Optional[int] = field(init=False)
    _server_status: Optional[Status.ValueType] = field(init=False)

    def __post_init__(self) -> None:
        """Initialize game client and websocket from player configuration."""
        self._client = GameClient(self._player.client_configuration)
        self._messenger = Messenger(
            self._player.client_configuration.sc2_api_address,
            self._player.client_configuration.sc2_api_port,
        )
        self._player_id = None
        self._server_status = None

    async def launch_sc2(self) -> None:
        """Launch an instance of the StarCraft II client for the controller."""
        # TODO: Make this method a no-op if called when Controller is configured
        # for ladder play. Assertions are crude.
        assert self._client is not None
        self._client.launch()
        LOGGER.debug("StarCraft II launched for controller.", controller=self)

    async def connect(self) -> None:
        """Establish connection to the StarCraft II API server."""
        await self._messenger.connect_server()
        await self._update_server_status()
        await self._validate_server_status(Status.launched)

        LOGGER.debug("Controller connected to StarCraft II API.", controller=self)

    async def create_match(self, match_configuration: Match) -> None:
        """Creates a StarCraft II match for players to join.

        Args:
            match_configuration: StarCraft II match to create.

        For any given match, only one Controller should create a match.

        """
        response = await self._messenger.create_game(match_configuration)
        await self._update_server_status(response)
        await self._validate_server_status(Status.init_game)

        LOGGER.debug("Controller create_game complete.", controller=self)

    async def join_match(self, port_configuration: Optional[MatchPortConfig]) -> None:
        """Join a StarCraft II match.

        Args:
            port_configuration: Multiplayer port configuration if the match is
                multiplayer, otherwise None.

        For any given match, all Controllers should join the match. The match will not
        begin until all participants have joined.

        """
        response = await self._messenger.join_player(self._player, port_configuration)

        await self._update_server_status(response)
        await self._validate_server_status(Status.in_game)

        # The StarCraft II API generates the _player_id upon joining, and is used to
        # decode the match results.
        response_join_game = response.message.join_game
        self._player_id = response_join_game.player_id

        LOGGER.debug("Controller join_game complete.", controller=self)

    # TODO: refactor for real time match:
    # on_step is automatically called by the API for a realtime match.
    async def play_match(self) -> Optional[MatchResult]:
        """Run a single step of the game loop.

        Returns:
            None if the match is still running, or MatchResult for the Controller's
            player if the match has ended.

        """
        # RequestObservation to check if game has ended.
        response = await self._messenger.request_observation()
        observation: ResponseObservation = response.message.observation
        await self._update_server_status(response)

        # Check if the match has ended, and return the match results.
        if self._server_status == Status.ended:
            result: PlayerResult = next(
                result
                for result in observation.player_result
                if result.player_id == self._player_id
            )

            LOGGER.debug("StarCraft II match has ended for Controller", controller=self)
            return MatchResult(result.player_id, result.result)

        # Next step
        await self._messenger.step_game()

    async def clean_up(self) -> None:
        """Clean up controller resources.

        Although quit_game can be used to trigger cleanup of the SC2 instance, use
        this method to ensure the process is terminated.

        """
        LOGGER.debug("Triggering Controller cleanup.", controller=self)
        await self._messenger.terminate()
        self._client.terminate()

    async def leave_match(self) -> None:
        """Leave the StarCraft II match.

        The StarCraft II client will continue running and revert to Status.launched.

        """
        leave_game = await self._messenger.leave_game()
        await self._update_server_status(leave_game)
        await self._validate_server_status(Status.launched)
        LOGGER.debug("Controller leave_match complete.", controller=self)

    async def quit_game(self) -> None:
        """Shutdown the StarCraft II client.

        SC2 will initiate shutdown, indicated by a Status.quit response status.

        """
        quit_game = await self._messenger.quit()
        await self._update_server_status(quit_game)
        await self._validate_server_status(Status.quit)
        LOGGER.debug("Controller quit_game complete.", controller=self)

    async def _update_server_status(
        self, response: Optional[ResponseMessage] = None
    ) -> None:
        """Update server status from a given response, or ping the server to get one.

        All responses from the StarCraft II API return the server status on response.
        The sole exception being when establishing a websocket connection to the API,
        no response is given - so ping the server instead.

        Args:
            response: Response from StarCraft II API to update the server status with.

        """
        if response is None:
            response = await self._messenger.ping_server()

        # Only log changes in the server status.
        status = response.status
        if status != self._server_status:
            LOGGER.debug(
                "StarCraft II API server status updated.",
                old_status=self._server_status,
                new_status=status,
            )
        self._server_status = status

    async def _validate_server_status(self, expected_status: Status.ValueType) -> None:
        """Validate and report the expected server status.

        Args:
            expected: Expected server status.

        Do not forcibly exit on a bad server status - but as this is internal to
        pycraft2 if an invalid state is reached it is likely a fatal error is imminent.

        """
        if self._server_status != expected_status:
            LOGGER.error(
                "Unexpected StarCraft II API server status.",
                expected_status=expected_status,
                current_status=self._server_status,
            )
        LOGGER.debug(
            "StarCraft II API server status OK.",
            expected_status=expected_status,
            current_status=self._server_status,
        )
