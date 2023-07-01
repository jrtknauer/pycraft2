"""Transport interface for communicating with the StarCraft II API server.

Public classes:
    Messenger

"""

from dataclasses import InitVar, dataclass, field
from typing import Optional

import structlog

from pycraft2.match import Match
from pycraft2.message import (
    InterfaceOptionsMessage,
    PlayerSetupMessage,
    PortSetMessage,
    RequestCreateGameMessage,
    RequestJoinGameMessage,
    RequestLeaveGameMessage,
    RequestMessage,
    RequestObservationMessage,
    RequestPingMessage,
    RequestQuitMessage,
    RequestStepMessage,
    Response,
    ResponseMessage,
)
from pycraft2.player import Bot, Computer, Player
from pycraft2.port import MatchPortConfig
from pycraft2.s2clientprotocol.sc2api_pb2 import Status
from pycraft2.websocket import Websocket

LOGGER = structlog.get_logger(__name__)


@dataclass(slots=True)
class Messenger:
    """StarCraft II API communication interfaces.

    Attributes:
        _ws: Websocket instance to communicate with the StarCraft II API.
        _ws: Bound logger for logging requests and responses.

    aiohttp does not log sending or receiving messages (presumably not to burden
    library users with potential performance penalities for bad logging
    configuration). pycraft2 should still log all StarCraft II API requests and
    responses, with an eventual production toggle to disable logging if the overhead
    is impeding library performance.

    """

    sc2_api_address: InitVar[str]
    sc2_api_port: InitVar[int]
    _ws: Websocket = field(init=False)
    _logger: structlog.BoundLogger = field(init=False)

    def __post_init__(self, sc2_api_address: str, sc2_api_port: int) -> None:
        """Instantiate the Websocket.

        Args:
            sc2_api_address: The IPv4 address for the StarCraft II API server.
            sc2_api_port: The port for the StarCraft II API server.

        """
        self._ws = Websocket(sc2_api_address, sc2_api_port)
        self._logger = LOGGER.bind()

    async def connect_server(self) -> None:
        """Connect to the StarCraft II API server."""
        await self._ws.connect()

    async def ping_server(self) -> ResponseMessage:
        """Ping the StarCraft II API server and wait for the Response.

        Returns:
            ResponseMessage instance wrapping the API Response.

        """
        # Prepare the Request.
        ping = RequestPingMessage()
        request = RequestMessage(ping.message)

        await self._ws.send_request(request)
        return await self._get_response()

    async def create_game(self, match_configuration: Match) -> ResponseMessage:
        """Request the creation of a match and wait for the Response.

        Args:
            match_configuration: StarCraft II match configuration for creating a match.

        Returns:
            ResponseMessage instance wrapping the ResponseCreateGame API Response.

        """
        # Player setup differs between Computers and Participants (scripted bots).
        player_setups: list[PlayerSetupMessage] = []
        for player in match_configuration.players:
            match player:
                case Bot():
                    player_setup = PlayerSetupMessage.participant(
                        player.race, player.name
                    )
                    player_setups.append(player_setup)
                case Computer():
                    player_setup = PlayerSetupMessage.computer(
                        player.race, player.ai_difficulty, player.ai_build
                    )
                    player_setups.append(player_setup)

        # Prepare the Request.
        request_create_game = RequestCreateGameMessage(
            match_configuration.map, player_setups
        )
        request = RequestMessage(request_create_game.message)

        await self._ws.send_request(request)
        return await self._get_response()

    async def join_player(
        self, player: Player, port_configuration: Optional[MatchPortConfig]
    ) -> ResponseMessage:
        """Request to join the match for a player and wait for the Response.

        Args:
            player: player configuration for the joining player.
            port_config: port configuration if the match is multiplayer.

        Returns:
            ResponseMessage instance wrapping the ResponseJoinGame API Response.

        """
        # pycraft2 supports the raw API interface.
        options = InterfaceOptionsMessage.raw_data()

        # Prepare multiplayer ports.
        if port_configuration is not None:
            server_ports = PortSetMessage(
                port_configuration.host_ports.game_port,
                port_configuration.host_ports.base_port,
            )
            client_ports = [
                PortSetMessage(
                    port_configuration.client_ports[i].game_port,
                    port_configuration.client_ports[i].base_port,
                )
                for i in range(len(port_configuration.client_ports))
            ]
        else:
            server_ports = PortSetMessage.omit()
            client_ports = [PortSetMessage.omit()]

        # Prepare the Request.
        request_join_game = RequestJoinGameMessage(
            race=player.race,
            observed_player_id=None,
            options=options,
            server_ports=server_ports,
            client_ports=client_ports,
            player_name=player.name,
        )
        request = RequestMessage(request_join_game.message)

        await self._ws.send_request(request)
        return await self._get_response()

    async def request_observation(self) -> ResponseMessage:
        """Request an observation of the game state and wait for the Response.

        Returns:
            ResponseMessage wrapping the ResponseObservation API Response.

        """
        # Prepare the Request.
        request_observation = RequestObservationMessage()
        request = RequestMessage(request_observation.message)

        await self._ws.send_request(request)
        return await self._get_response()

    async def step_game(self) -> ResponseMessage:
        """Request the next game loop and wait for the Response.

        Returns:
            ResponseMessage wrapping the ResponseStep API Response.

        """
        # Prepare the Request
        request_step = RequestStepMessage(count=100)
        request = RequestMessage(request_step.message)

        await self._ws.send_request(request)
        return await self._get_response()

    async def leave_game(self) -> ResponseMessage:
        """Request to leave the match and wait for the Response.

        Returns:
            ResponseMessage wrapping the ResponseLeaveGame API Response.

        """
        # Prepare the Request.
        request_leave_game = RequestLeaveGameMessage()
        request = RequestMessage(request_leave_game.message)

        await self._ws.send_request(request)
        return await self._get_response()

    async def quit(self) -> ResponseMessage:
        """Request to shut down the StarCraft II client and wait for the response.

        Returns:
            ResponseMessage wrapping the ResponseQuit API Response.

        """
        # Prepare the Request.
        request_quit = RequestQuitMessage()
        request = RequestMessage(request_quit.message)

        await self._ws.send_request(request)
        return await self._get_response()

    async def terminate(self) -> None:
        """Close the websocket connection with the StarCraft II API."""
        await self._ws.close_connection()

    async def _get_response(self) -> ResponseMessage:
        """Receive, wrap, and return a response from the StarCraft II API.

        Returns:
            ResponseMessage wrapping an API Response.

        """
        response = Response()
        response.ParseFromString(await self._ws.receive_response())

        # Do not raise errors here, the Status.unknown server status behavior is not
        # well defined. Only report the error and let the controllers handle any
        # runtime errors that manifest.
        if response.status == Status.unknown:
            self._logger.error(
                "Received unknown StarCraft II API server status.", response=response
            )

        return ResponseMessage(response)
