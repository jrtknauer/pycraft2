"""Interface for websocket communication with the StarCraft II API.

Public classes:
    Websocket

"""

from dataclasses import InitVar, dataclass, field
from typing import ClassVar, Optional

import backoff
import structlog
from aiohttp import ClientConnectionError, ClientSession, ClientWebSocketResponse

from pycraft2.message import RequestMessage

LOGGER = structlog.get_logger(__name__)


@dataclass(slots=True)
class Websocket:
    """Websocket communication interface for the StarCraft II API.

    Attributes:
        _connect_timeout: Websocket timeout interval in seconds.
        _ws_url: StarCraft II API connection URL.
        _session: Client session for websocket communication.
        _ws: Handle for websocket connection.
        _logger: Bound logger for requests and responses.

    """

    _connect_timeout: ClassVar[int] = 100

    sc2_api_address: InitVar[str]
    sc2_api_port: InitVar[int]

    _ws_url: str = field(init=False)
    _session: ClientSession = field(init=False)
    _ws: Optional[ClientWebSocketResponse] = field(init=False)
    _logger: structlog.BoundLogger = field(init=False)

    def __post_init__(self, sc2_api_address: str, sc2_api_port: int) -> None:
        """Initialize internal attributes."""
        self._ws_url = f"ws://{sc2_api_address}:{sc2_api_port}/sc2api"
        self._session = ClientSession()
        self._ws = None
        self._logger = LOGGER.bind()

    async def connect(self) -> None:
        """Establish websocket communication with the StarCraft II API server."""

        def _backoff_handler(details: dict[str, str]) -> None:
            """Log on retry."""
            LOGGER.debug(
                "Failed to connect to StarCraft II API server, retrying.",
                details=details,
            )

        async def _giveup_handler(details: dict[str, str]) -> None:
            """Log connection timeout."""
            LOGGER.critical(
                "Failed to connec to StarCraft II API server, giving up.",
                details=details,
            )

        @backoff.on_exception(
            backoff.constant,
            ClientConnectionError,
            max_time=self._connect_timeout,
            on_backoff=_backoff_handler,  # type: ignore
            on_giveup=_giveup_handler,  # type: ignore
        )
        async def _connect() -> ClientWebSocketResponse:
            """Connect to the StarCraft II API server and retry on failure.

            Returns:
                Handle for the websocket connection.

            Raises:
                ClientConnectionError on connection failure. If within the backoff
                max_time interval, the exception will be caught and _connect() will
                retry instead.

            """
            ws = await self._session.ws_connect(  # pyright: ignore[reportUnknownMemberType]  # noqa: E501
                self._ws_url
            )
            return ws

        try:
            self._ws = await _connect()
        except ClientConnectionError as e:
            raise RuntimeError(e)

        LOGGER.debug("Connected to the StarCraft II API.", url=self._ws_url)

    async def send_request(self, message: RequestMessage) -> None:
        """Send Request protocol buffer message to the StarCraft II API."""
        await self._ws.send_bytes(  # pyright: ignore[reportOptionalMemberAccess]  # noqa: E501
            message.serialized
        )

    async def receive_response(self) -> bytes:
        """Receive Response protocol buffer message from StarCraft II API.

        Returns:
            StarCraft II API Response binary data.

        """
        return (
            await self._ws.receive_bytes()  # pyright: ignore[reportOptionalMemberAccess]  # noqa: E501
        )

    async def close_connection(self) -> None:
        """Close the websocket client session."""
        LOGGER.debug("Closing connection to StarCraft II API server.")
        if self._ws and not self._ws.closed:
            await self._ws.close()

        if self._session and not self._session.closed:
            await self._session.close()
