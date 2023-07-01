"""
@generated by mypy-protobuf.  Do not edit manually!
isort:skip_file
"""
import builtins
import collections.abc
import google.protobuf.descriptor
import google.protobuf.internal.containers
import google.protobuf.message
import s2clientprotocol.common_pb2
import s2clientprotocol.error_pb2
import sys

if sys.version_info >= (3, 8):
    import typing as typing_extensions
else:
    import typing_extensions

DESCRIPTOR: google.protobuf.descriptor.FileDescriptor

class RequestQuery(google.protobuf.message.Message):
    DESCRIPTOR: google.protobuf.descriptor.Descriptor

    PATHING_FIELD_NUMBER: builtins.int
    ABILITIES_FIELD_NUMBER: builtins.int
    PLACEMENTS_FIELD_NUMBER: builtins.int
    IGNORE_RESOURCE_REQUIREMENTS_FIELD_NUMBER: builtins.int
    @property
    def pathing(self) -> google.protobuf.internal.containers.RepeatedCompositeFieldContainer[global___RequestQueryPathing]: ...
    @property
    def abilities(self) -> google.protobuf.internal.containers.RepeatedCompositeFieldContainer[global___RequestQueryAvailableAbilities]: ...
    @property
    def placements(self) -> google.protobuf.internal.containers.RepeatedCompositeFieldContainer[global___RequestQueryBuildingPlacement]: ...
    ignore_resource_requirements: builtins.bool
    """Ignores requirements like food, minerals and so on."""
    def __init__(
        self,
        *,
        pathing: collections.abc.Iterable[global___RequestQueryPathing] | None = ...,
        abilities: collections.abc.Iterable[global___RequestQueryAvailableAbilities] | None = ...,
        placements: collections.abc.Iterable[global___RequestQueryBuildingPlacement] | None = ...,
        ignore_resource_requirements: builtins.bool | None = ...,
    ) -> None: ...
    def HasField(self, field_name: typing_extensions.Literal["ignore_resource_requirements", b"ignore_resource_requirements"]) -> builtins.bool: ...
    def ClearField(self, field_name: typing_extensions.Literal["abilities", b"abilities", "ignore_resource_requirements", b"ignore_resource_requirements", "pathing", b"pathing", "placements", b"placements"]) -> None: ...

global___RequestQuery = RequestQuery

class ResponseQuery(google.protobuf.message.Message):
    DESCRIPTOR: google.protobuf.descriptor.Descriptor

    PATHING_FIELD_NUMBER: builtins.int
    ABILITIES_FIELD_NUMBER: builtins.int
    PLACEMENTS_FIELD_NUMBER: builtins.int
    @property
    def pathing(self) -> google.protobuf.internal.containers.RepeatedCompositeFieldContainer[global___ResponseQueryPathing]: ...
    @property
    def abilities(self) -> google.protobuf.internal.containers.RepeatedCompositeFieldContainer[global___ResponseQueryAvailableAbilities]: ...
    @property
    def placements(self) -> google.protobuf.internal.containers.RepeatedCompositeFieldContainer[global___ResponseQueryBuildingPlacement]: ...
    def __init__(
        self,
        *,
        pathing: collections.abc.Iterable[global___ResponseQueryPathing] | None = ...,
        abilities: collections.abc.Iterable[global___ResponseQueryAvailableAbilities] | None = ...,
        placements: collections.abc.Iterable[global___ResponseQueryBuildingPlacement] | None = ...,
    ) -> None: ...
    def ClearField(self, field_name: typing_extensions.Literal["abilities", b"abilities", "pathing", b"pathing", "placements", b"placements"]) -> None: ...

global___ResponseQuery = ResponseQuery

class RequestQueryPathing(google.protobuf.message.Message):
    """--------------------------------------------------------------------------------------------------"""

    DESCRIPTOR: google.protobuf.descriptor.Descriptor

    START_POS_FIELD_NUMBER: builtins.int
    UNIT_TAG_FIELD_NUMBER: builtins.int
    END_POS_FIELD_NUMBER: builtins.int
    @property
    def start_pos(self) -> s2clientprotocol.common_pb2.Point2D: ...
    unit_tag: builtins.int
    @property
    def end_pos(self) -> s2clientprotocol.common_pb2.Point2D: ...
    def __init__(
        self,
        *,
        start_pos: s2clientprotocol.common_pb2.Point2D | None = ...,
        unit_tag: builtins.int | None = ...,
        end_pos: s2clientprotocol.common_pb2.Point2D | None = ...,
    ) -> None: ...
    def HasField(self, field_name: typing_extensions.Literal["end_pos", b"end_pos", "start", b"start", "start_pos", b"start_pos", "unit_tag", b"unit_tag"]) -> builtins.bool: ...
    def ClearField(self, field_name: typing_extensions.Literal["end_pos", b"end_pos", "start", b"start", "start_pos", b"start_pos", "unit_tag", b"unit_tag"]) -> None: ...
    def WhichOneof(self, oneof_group: typing_extensions.Literal["start", b"start"]) -> typing_extensions.Literal["start_pos", "unit_tag"] | None: ...

global___RequestQueryPathing = RequestQueryPathing

class ResponseQueryPathing(google.protobuf.message.Message):
    DESCRIPTOR: google.protobuf.descriptor.Descriptor

    DISTANCE_FIELD_NUMBER: builtins.int
    distance: builtins.float
    """0 if no path exists"""
    def __init__(
        self,
        *,
        distance: builtins.float | None = ...,
    ) -> None: ...
    def HasField(self, field_name: typing_extensions.Literal["distance", b"distance"]) -> builtins.bool: ...
    def ClearField(self, field_name: typing_extensions.Literal["distance", b"distance"]) -> None: ...

global___ResponseQueryPathing = ResponseQueryPathing

class RequestQueryAvailableAbilities(google.protobuf.message.Message):
    """--------------------------------------------------------------------------------------------------"""

    DESCRIPTOR: google.protobuf.descriptor.Descriptor

    UNIT_TAG_FIELD_NUMBER: builtins.int
    unit_tag: builtins.int
    def __init__(
        self,
        *,
        unit_tag: builtins.int | None = ...,
    ) -> None: ...
    def HasField(self, field_name: typing_extensions.Literal["unit_tag", b"unit_tag"]) -> builtins.bool: ...
    def ClearField(self, field_name: typing_extensions.Literal["unit_tag", b"unit_tag"]) -> None: ...

global___RequestQueryAvailableAbilities = RequestQueryAvailableAbilities

class ResponseQueryAvailableAbilities(google.protobuf.message.Message):
    DESCRIPTOR: google.protobuf.descriptor.Descriptor

    ABILITIES_FIELD_NUMBER: builtins.int
    UNIT_TAG_FIELD_NUMBER: builtins.int
    UNIT_TYPE_ID_FIELD_NUMBER: builtins.int
    @property
    def abilities(self) -> google.protobuf.internal.containers.RepeatedCompositeFieldContainer[s2clientprotocol.common_pb2.AvailableAbility]: ...
    unit_tag: builtins.int
    unit_type_id: builtins.int
    def __init__(
        self,
        *,
        abilities: collections.abc.Iterable[s2clientprotocol.common_pb2.AvailableAbility] | None = ...,
        unit_tag: builtins.int | None = ...,
        unit_type_id: builtins.int | None = ...,
    ) -> None: ...
    def HasField(self, field_name: typing_extensions.Literal["unit_tag", b"unit_tag", "unit_type_id", b"unit_type_id"]) -> builtins.bool: ...
    def ClearField(self, field_name: typing_extensions.Literal["abilities", b"abilities", "unit_tag", b"unit_tag", "unit_type_id", b"unit_type_id"]) -> None: ...

global___ResponseQueryAvailableAbilities = ResponseQueryAvailableAbilities

class RequestQueryBuildingPlacement(google.protobuf.message.Message):
    """--------------------------------------------------------------------------------------------------"""

    DESCRIPTOR: google.protobuf.descriptor.Descriptor

    ABILITY_ID_FIELD_NUMBER: builtins.int
    TARGET_POS_FIELD_NUMBER: builtins.int
    PLACING_UNIT_TAG_FIELD_NUMBER: builtins.int
    ability_id: builtins.int
    @property
    def target_pos(self) -> s2clientprotocol.common_pb2.Point2D: ...
    placing_unit_tag: builtins.int
    """Not required"""
    def __init__(
        self,
        *,
        ability_id: builtins.int | None = ...,
        target_pos: s2clientprotocol.common_pb2.Point2D | None = ...,
        placing_unit_tag: builtins.int | None = ...,
    ) -> None: ...
    def HasField(self, field_name: typing_extensions.Literal["ability_id", b"ability_id", "placing_unit_tag", b"placing_unit_tag", "target_pos", b"target_pos"]) -> builtins.bool: ...
    def ClearField(self, field_name: typing_extensions.Literal["ability_id", b"ability_id", "placing_unit_tag", b"placing_unit_tag", "target_pos", b"target_pos"]) -> None: ...

global___RequestQueryBuildingPlacement = RequestQueryBuildingPlacement

class ResponseQueryBuildingPlacement(google.protobuf.message.Message):
    DESCRIPTOR: google.protobuf.descriptor.Descriptor

    RESULT_FIELD_NUMBER: builtins.int
    result: s2clientprotocol.error_pb2.ActionResult.ValueType
    def __init__(
        self,
        *,
        result: s2clientprotocol.error_pb2.ActionResult.ValueType | None = ...,
    ) -> None: ...
    def HasField(self, field_name: typing_extensions.Literal["result", b"result"]) -> builtins.bool: ...
    def ClearField(self, field_name: typing_extensions.Literal["result", b"result"]) -> None: ...

global___ResponseQueryBuildingPlacement = ResponseQueryBuildingPlacement
