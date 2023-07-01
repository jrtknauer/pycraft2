"""Test the pycraft2.client module.

GameClient is tested primarily through integration tests, as its sole function is to
launch and terminate a StarCraft II instance.

"""

from pycraft2.client import (
    _ClientArgumentBuilder,  # pyright: ignore[reportPrivateUsage]
)
from pycraft2.client import _SC2Arg, _SC2Flag  # pyright: ignore[reportPrivateUsage]
from pycraft2.player import PlayerClientConfiguration


class TestClientArgumentBuilder:
    """Test the _ClientArgumentBuilder class."""

    def test_args(self) -> None:
        """Verify all argument are present with a value.

        Argument value correctness is provided by the PlayerClientConfiguration
        interface.

        """
        args = _ClientArgumentBuilder(PlayerClientConfiguration()).args()

        for enumeration in _SC2Arg:
            assert enumeration.value in args

        assert len(args) == (len(_SC2Arg) * 2)

    def test_verbose(self) -> None:
        """Verify verbose is present alongside the other arguments."""
        args = _ClientArgumentBuilder(PlayerClientConfiguration(verbose=True)).args()

        assert _SC2Flag.VERBOSE.value in args

        assert len(args) == (len(_SC2Arg) * 2) + 1
