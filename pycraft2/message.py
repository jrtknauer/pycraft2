"""Interfaces for the s2clientprotocol API.

Even though the API is static, use interfaces instead of the API directly for re-use
and correctness purposes. As an example, sc2api_b2.PlayerSetup appears to be a fairly
simple message:

https://github.com/Blizzard/s2client-proto/blob/master/s2clientprotocol/sc2api.proto#L544
message PlayerSetup {
    optional PlayerType type = 1;

    // Only used for a computer player.
    optional Race race = 2;
    optional Difficulty difficulty = 3;
    optional string player_name = 4;
    optional AIBuild ai_build = 5;
}

But where should the logic to correctly instantiate a PlayerSetup message reside?
What about validation? If the message is used in more than one source file, but the
validation differs between different PlayerTypes, how can usage remain consistent?

While requiring a great deal of boilerplate and verbosity, wrapping the API is a
sensible option to ensure the implied logic of the API is encoded into the interfaces
themselves.

"""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import InitVar, dataclass, field
from typing import Any, Optional

from pycraft2.map import Map
from pycraft2.s2clientprotocol.common_pb2 import Race
from pycraft2.s2clientprotocol.sc2api_pb2 import (
    AIBuild,
    Difficulty,
    InterfaceOptions,
    LocalMap,
    PlayerSetup,
    PlayerType,
    PortSet,
    Request,
    RequestCreateGame,
    RequestJoinGame,
    RequestLeaveGame,
    RequestObservation,
    RequestPing,
    RequestQuit,
    RequestStep,
    Response,
    SpatialCameraSetup,
    Status,
)


@dataclass(slots=True)
class _ProtocolMessage(ABC):
    """StarCraft II API message wrapper interface.

    Attributes:
        _message: StarCraft II API protocol buffer message.

    Classes which implement this interface should return the instantiated protocol
    buffer message via the message property - or None if the message is omitted.

    """

    _message: Optional[Any] = field(init=False)

    @property
    @abstractmethod
    def message(self) -> Optional[Any]:
        """Overrides should return self._message.

        Have children implement the property instead of inherit from the base class
        so return types are not ambiguous - there are limits to the protocol buffer
        type stubs when it comes to inheritance.

        While there is a performance penalty for accessing _message via a property, it
        is somewhat mitigated by __slots__, and is not significant enough to drop
        interface enforcement.

        """
        raise NotImplementedError


@dataclass(slots=True)
class InterfaceOptionsMessage(_ProtocolMessage):
    """Wraps the InterfaceOptions protocol buffer message.

    # TODO: does show_* options matter for the raw interface? Probably not, but
    # the s2client-proto comment for show_placeholders indicates otherwise.
    InitVar:
        raw: Toggle for the raw interface.
        score: Toggle for the score interface.
        feature_layer: Feature layers configuration.
        render: Render layer configuration.
        show_cloaked: Show some detail for cloaked units.
        show_burrowed: Show some shadows for burrowed units.
        show_placeholders: Return placeholder units for raw and feature players.
        raw_affects selection: Toggle for how raw actions execute.
        raw_crop_to_playable_area: Toggle for raw.proto coordinates relative to the
            playable area.

    Attributes:
        _message: InterfaceOptions protocol buffer message.

    Protocol buffer schema:
    https://github.com/Blizzard/s2client-proto/blob/master/s2clientprotocol/sc2api.proto#L564

    """

    raw: InitVar[bool]
    score: InitVar[bool]
    feature_layer: InitVar[SpatialCameraSetupMessage]
    render: InitVar[SpatialCameraSetupMessage]
    show_cloaked: InitVar[bool]
    show_burrowed_shadows: InitVar[bool]
    show_placeholders: InitVar[bool]
    raw_affects_selection: InitVar[bool]
    raw_crop_to_playable_area: InitVar[bool]

    _message: InterfaceOptions = field(init=False)

    def __post_init__(
        self,
        raw: bool,
        score: bool,
        feature_layer: SpatialCameraSetupMessage,
        render: SpatialCameraSetupMessage,
        show_cloaked: bool,
        show_burrowed_shadows: bool,
        show_placeholders: bool,
        raw_affects_selection: bool,
        raw_crop_to_playable_area: bool,
    ) -> None:
        """Initialize _message from InitVars."""
        self._message = InterfaceOptions(
            raw=raw,
            score=score,
            feature_layer=feature_layer.message,
            render=render.message,
            show_cloaked=show_cloaked,
            show_burrowed_shadows=show_burrowed_shadows,
            show_placeholders=show_placeholders,
            raw_affects_selection=raw_affects_selection,
            raw_crop_to_playable_area=raw_crop_to_playable_area,
        )

    @classmethod
    def raw_data(cls) -> InterfaceOptionsMessage:
        """Instantiate an InterfaceOptionsMessage suitable for raw interactions.

        Returns:
            InterFaceOptionsMessage configured for the raw interactions interface.

        https://github.com/Blizzard/s2client-proto/blob/master/docs/protocol.md#raw-data

        """
        return cls(
            raw=True,
            score=True,
            feature_layer=SpatialCameraSetupMessage.omit(),
            render=SpatialCameraSetupMessage.omit(),
            show_cloaked=True,
            show_burrowed_shadows=True,
            show_placeholders=True,
            raw_affects_selection=True,
            raw_crop_to_playable_area=False,
        )

    @property
    def message(self) -> InterfaceOptions:
        return self._message


@dataclass(slots=True)
class LocalMapMessage(_ProtocolMessage):
    """Wraps the LocalMap protocol buffer message.

    InitVar:
        map: Map instance with a valid map path.

    Attributes:
        _message: LocalMap protocol buffer message using map_data.

    Notes on map_data instead of map_path:

    There is undocumented behavior for the StarCraft II API when StarCraft II is
    installed in the default directory for the system. For this scenario, even if a
    valid absolute path for the map is provided, the StarCraft II API will mangle the
    path expecting it to be in the maps/ directory; default installations use Maps/
    (uppercase) directory. Instead of requiring users to symlink maps, pycraft2
    circumvents this by loading the binary data for the map directory. The
    StarCraft II API will generate a temporary map file from this data and use it to
    play the match.

    Protocol buffer schema:
    https://github.com/Blizzard/s2client-proto/blob/master/s2clientprotocol/sc2api.proto#L184

    """

    map: InitVar[Map]
    _message: LocalMap = field(init=False)

    def __post_init__(self, map: Map) -> None:
        """Instantiate _message from InitVars."""
        self._message = LocalMap(map_data=map.data)

    @property
    def message(self) -> LocalMap:
        return self._message


@dataclass(slots=True)
class PortSetMessage(_ProtocolMessage):
    """Wraps the PortSet protocol buffer message.

    InitVar:
        game_port: Game port to assign to PortSet.
        base_port: Base port to assign to PortSet.

    Attributes:
        _message: PortSet protocol buffer message, or None if the message is omitted.

    Protocol buffer schema:
    https://github.com/Blizzard/s2client-proto/blob/master/s2clientprotocol/sc2api.proto#L225

    """

    game_port: InitVar[Optional[int]] = None
    base_port: InitVar[Optional[int]] = None
    _message: Optional[PortSet] = field(init=False)

    def __post_init__(self, game_port: Optional[int], base_port: Optional[int]) -> None:
        """Initialize _message from InitVars.

        The @classmethod omit provides an interface for disabling this message; if both
        game_port and base_port are set to None, no message should be created.

        """
        if game_port is None and base_port is None:
            self._message = None
        else:
            self._message = PortSet(game_port=game_port, base_port=base_port)

    @classmethod
    def omit(cls) -> PortSetMessage:
        """Instantiates such that the message property returns None.

        Returns:
            PortSetMessage with no message data, the message property will return None.

        """
        return PortSetMessage(None, None)

    @property
    def message(self) -> Optional[PortSet]:
        return self._message


@dataclass(slots=True)
class RequestJoinGameMessage(_ProtocolMessage):
    """Wraps the RequestJoinGame protocol buffer message.

    InitVars:
        options: InterfaceOptionsMessage instance for the match.
        server_ports: PortSetMessage instance for the match.
        client_ports: List of PortSetMessage instances for the match.
        race: Race enumeration to play for the match, or None.
        observed_player_id: Observer player ID for the match, or None.
        player_name: The player name to join that game as, or None.
        host_ip: Disabled, do not support remote play.

    Attributes:
        _message: RequestJoinGame protocol buffer message.

    Protocol buffer schema:
    https://github.com/Blizzard/s2client-proto/blob/master/s2clientprotocol/sc2api.proto#L210

    """

    options: InitVar[InterfaceOptionsMessage]
    server_ports: InitVar[PortSetMessage]
    client_ports: InitVar[list[PortSetMessage]]
    race: InitVar[Optional[Race.ValueType]] = None
    observed_player_id: InitVar[Optional[int]] = None
    player_name: InitVar[Optional[str]] = None
    host_ip: InitVar[Optional[str]] = None
    _message: RequestJoinGame = field(init=False)

    def __post_init__(
        self,
        options: InterfaceOptionsMessage,
        server_ports: PortSetMessage,
        client_ports: list[PortSetMessage],
        race: Optional[Race.ValueType],
        observed_player_id: Optional[int],
        player_name: Optional[str],
        host_ip: Optional[str] = None,
    ) -> None:
        """Initialize _message from InitVars.

        client_ports cannot be assigned to directly and must instead be extended as a
        repeated field.

        """
        self._message = RequestJoinGame(
            race=race,
            observed_player_id=observed_player_id,
            options=options.message,
            server_ports=server_ports.message,
            player_name=player_name,
            host_ip=host_ip,
        )

        # https://protobuf.dev/reference/python/python-generated/#repeated-fields
        self._message.client_ports.extend(
            [m.message for m in client_ports if m.message is not None]
        )

    @property
    def message(self) -> RequestJoinGame:
        return self._message


@dataclass(slots=True)
class PlayerSetupMessage(_ProtocolMessage):
    """Wraps the PlayerSetup protocol buffer message.

    InitVars:
        player_type: Type of player to join the match.
        race: Race of the player, or None if an Observer.
        difficulty: AI difficulty level, only set if a Computer.
        player_name: Name to join the match with.
        ai_build: AI build order to execute, only set if a Computer.

    Attributes:
        _message: PlayerSetup protocol buffer message.

    Prefer to use the @classmethod constructors to correctly instantiate defaults
    depending on the player_type.

    Protocol buffer schema:
    https://github.com/Blizzard/s2client-proto/blob/master/s2clientprotocol/sc2api.proto#L544

    """

    player_type: InitVar[PlayerType.ValueType]
    race: InitVar[Optional[Race.ValueType]]
    difficulty: InitVar[Optional[Difficulty.ValueType]]
    player_name: InitVar[Optional[str]]
    ai_build: InitVar[Optional[AIBuild.ValueType]]
    _message: PlayerSetup = field(init=False)

    def __post_init__(
        self,
        player_type: PlayerType.ValueType,
        race: Optional[Race.ValueType],
        difficulty: Optional[Difficulty.ValueType],
        player_name: Optional[str],
        ai_build: Optional[AIBuild.ValueType],
    ) -> None:
        """Initialize _message from InitVars."""
        self._message = PlayerSetup(
            type=player_type,
            race=race,
            difficulty=difficulty,
            player_name=player_name,
            ai_build=ai_build,
        )

    @classmethod
    def participant(
        cls, race: Race.ValueType, player_name: Optional[str] = None
    ) -> PlayerSetupMessage:
        """Instantiate PlayerSetup for a Participant.

        Returns:
            PlayerSetupMessage for a Participant.

        """
        return cls(
            player_type=PlayerType.Participant,
            race=race,
            difficulty=None,
            player_name=player_name,
            ai_build=None,
        )

    @classmethod
    def computer(
        cls,
        race: Race.ValueType,
        difficulty: Difficulty.ValueType,
        ai_build: AIBuild.ValueType,
        player_name: Optional[str] = None,
    ) -> PlayerSetupMessage:
        """Instantiate PlayerSetup for a Computer.

        Returns:
            PlayerSetupMessage for a Computer.

        """
        return cls(
            player_type=PlayerType.Computer,
            race=race,
            difficulty=difficulty,
            player_name=player_name,
            ai_build=ai_build,
        )

    @property
    def message(self) -> PlayerSetup:
        return self._message


@dataclass(slots=True)
class RequestCreateGameMessage(_ProtocolMessage):
    """Wraps the RequestCreateGame protocol buffer message.

    InitVars:
        local_map: Map instance for the map to play the match with.
        player_setups: PlayerSetupMessage instances to create the game for.
        disable_fog: Boolean setting for fog-of-war.
        random_seed: Optional random seed setting for pseudorandom in-game animations.
        real_time: Boolean setting for playing the match in real time.

    Attributes:
        _message: RequestCreateGame protocol buffer message.

    Protocol buffer schema:
    https://github.com/Blizzard/s2client-proto/blob/master/s2clientprotocol/sc2api.proto#L170

    """

    local_map: InitVar[Map]
    player_setups: InitVar[list[PlayerSetupMessage]]
    disable_fog: InitVar[bool] = False
    random_seed: InitVar[Optional[int]] = None
    real_time: InitVar[bool] = False
    _message: RequestCreateGame = field(init=False)

    def __post_init__(
        self,
        map: Map,
        player_setups: list[PlayerSetupMessage],
        disable_fog: bool,
        random_seed: Optional[int],
        real_time: bool,
    ) -> None:
        """Initialize _message from InitVars.

        player_setup cannot be assigned to directly and must instead be extended as a
        repeated field.

        """
        self._message = RequestCreateGame(
            local_map=LocalMapMessage(map).message,
            disable_fog=disable_fog,
            random_seed=random_seed,
            realtime=real_time,
        )

        # https://protobuf.dev/reference/python/python-generated/#repeated-fields
        self._message.player_setup.extend([ps.message for ps in player_setups])

    @property
    def message(self) -> RequestCreateGame:
        return self._message


@dataclass(slots=True)
class RequestStepMessage(_ProtocolMessage):
    """Wraps the RequestStep protocol buffer message.

    InitVars:
        count: in-game frames to advance on step.

    Attributes:
        _message: RequestStep protocol buffer message.

    Protocol buffer schema:
    https://github.com/Blizzard/s2client-proto/blob/master/s2clientprotocol/sc2api.proto#L391

    """

    count: InitVar[Optional[int]] = None
    _message: RequestStep = field(init=False)

    def __post_init__(self, count: Optional[int]):
        """Initialize _message from InitVars."""
        self._message = RequestStep(count=count)

    @property
    def message(self) -> RequestStep:
        return self._message


@dataclass(slots=True)
class RequestMessage(_ProtocolMessage):
    """Wraps the Request protocol buffer message.

    InitVars:
        request: protocol buffer message to send as a Request message.

    Attributes:
        _message: Request protocol buffer message.
        serialized: Serialized Request data.

    Protocol buffer schema:
    https://github.com/Blizzard/s2client-proto/blob/master/s2clientprotocol/sc2api.proto#L84

    """

    request: InitVar[Optional[Any]]
    _message: Request = field(init=False)
    serialized: bytes = field(init=False)

    def __post_init__(self, request: Optional[Any]) -> None:
        """Initialize _message from the InitVars, then serialize for the websocket.

        Raises:
            RuntimeError: Invalid Request types should not be sent to the StarCraft II
                API server.

        """
        match request:
            case RequestCreateGame():
                message = Request(create_game=request)
            case RequestJoinGame():
                message = Request(join_game=request)
            case RequestLeaveGame():
                message = Request(leave_game=request)
            case RequestObservation():
                message = Request(observation=request)
            case RequestPing():
                message = Request(ping=request)
            case RequestStep():
                message = Request(step=request)
            case RequestQuit():
                message = Request(quit=request)
            case _:
                # Unhandled message type - this should never happen.
                # TODO: custom exception.
                raise RuntimeError()
        self._message = message  # pyright: ignore[reportIncompatibleMethodOverride]
        self.serialized = self._message.SerializeToString()

    @property
    def message(self) -> Request:
        return self._message


@dataclass(slots=True)
class RequestLeaveGameMessage(_ProtocolMessage):
    """Wraps the RequestLeaveGame protocol buffer message.

    Attributes:
        _message: RequestLeaveGame protocol buffer message.

    Protocol buffer schema:
    https://github.com/Blizzard/s2client-proto/blob/master/s2clientprotocol/sc2api.proto#L311

    """

    _message: RequestLeaveGame = field(init=False)

    def __init__(self) -> None:
        """Initialize default _message."""
        self._message = RequestLeaveGame()

    @property
    def message(self) -> RequestLeaveGame:
        return self._message


@dataclass(slots=True)
class RequestObservationMessage(_ProtocolMessage):
    """Wraps the RequestObservation protocol buffer message.

    # TODO: What happens when requesting an observation with fog disabled when the
    # match was created with fog enabled? Surely this will not work...

    InitVars:
        disable_fog: Boolean setting to request an observation with fog disabled, or
            None to disable my omission.
        game_loop: Game loop to request an observation for, see additional notes.

    Notes on game_loop:

    From the s2client-proto schema, the game_loop setting is ignored when not playing
    in real-time mode. For real-time, the request will only return once the specified
    game loop has been reached. This makes game_loop a *very dangerous* setting for
    real-time mode, as you can end up blocking on the response! While the interface is
    available, it is not advisable to use.

    Protocol buffer schema:
    https://github.com/Blizzard/s2client-proto/blob/master/s2clientprotocol/sc2api.proto#L354

    """

    disable_fog: InitVar[Optional[bool]] = None
    game_loop: InitVar[Optional[int]] = None
    _message: RequestObservation = field(init=False)

    def __post_init__(
        self, disable_fog: Optional[bool] = None, game_loop: Optional[int] = None
    ) -> None:
        """Initialize _message from InitVars."""
        self._message = RequestObservation(disable_fog=disable_fog, game_loop=game_loop)

    @property
    def message(self) -> RequestObservation:
        return self._message


@dataclass(slots=True)
class RequestPingMessage(_ProtocolMessage):
    """Wraps the RequestPing protocol buffer message.

    Attributes:
        _message: RequestPing protocol buffer message.

    Protocol buffer schema:
    https://github.com/Blizzard/s2client-proto/blob/master/s2clientprotocol/sc2api.proto#L493

    """

    _message: RequestPing = field(init=False)

    def __post_init__(self) -> None:
        """Initialize default _message."""
        self._message = RequestPing()

    @property
    def message(self) -> RequestPing:
        return RequestPing()


@dataclass(slots=True)
class RequestQuitMessage(_ProtocolMessage):
    """Wraps the RequestQuit protocol buffer message.

    Attributes:
        _message: RequestQuit protocol buffer message.

    Protocol buffer schema:
    https://github.com/Blizzard/s2client-proto/blob/master/s2clientprotocol/sc2api.proto#L334

    """

    _message: RequestQuit = field(init=False)

    def __init__(self) -> None:
        """Initialize default _message."""
        self._message = RequestQuit()

    @property
    def message(self) -> RequestQuit:
        return self._message


@dataclass(slots=True)
class ResponseMessage(_ProtocolMessage):
    """Wraps the Response protocol buffer message.

    Attributes:
        _message: Response protocol buffer message.
        status: The StarCraft II API server status for the Response.

    Protocol buffer schema:
    https://github.com/Blizzard/s2client-proto/blob/master/s2clientprotocol/sc2api.proto#L121

    """

    _message: Response
    status: Status.ValueType = field(init=False)

    def __post_init__(self) -> None:
        """Initialize status from _message."""
        self.status = self._message.status

    @property
    def message(self) -> Response:
        return self._message


@dataclass(slots=True)
class SpatialCameraSetupMessage(_ProtocolMessage):
    """Wraps the SpatialCameraSetup protocol buffer message.

    pycraft2 will not support the feature or render interfaces, so always omit.

    Protocol buffer schema:
    https://github.com/Blizzard/s2client-proto/blob/master/s2clientprotocol/sc2api.proto#L554

    """

    _message: None = None

    @property
    def message(self) -> Optional[SpatialCameraSetup]:
        return self._message

    @classmethod
    def omit(cls) -> SpatialCameraSetupMessage:
        """Instantiates the class such that the message property returns None."""
        return cls()
