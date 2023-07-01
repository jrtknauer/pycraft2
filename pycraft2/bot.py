from abc import ABC, abstractmethod
from dataclasses import dataclass


@dataclass(slots=True)
class _BotImplementation(ABC):
    """Internal implementation for scripted bots.

    Do not instantiate with this class or interact with private methods and attributes.

    """

    pass


@dataclass(slots=True)
class BotInterface(_BotImplementation):
    """Public interfaces for implementing a scripted bot."""

    @abstractmethod
    def on_step(self) -> None:
        """"""
        raise NotImplementedError
