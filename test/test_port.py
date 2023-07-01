"""Test the pycraft.port module."""

import pytest

from pycraft2.port import MatchPortConfig, PortSet


class TestMatchPortConfig:
    """Test the MatchPortConfig class."""

    @pytest.mark.parametrize(
        "start_port, expected_host_ports, expected_client_ports",
        [
            (0, PortSet(2, 3), [PortSet(4, 5)]),
            (5000, PortSet(5002, 5003), [PortSet(5004, 5005)]),
        ],
    )
    def test_start_port(
        self,
        start_port: int,
        expected_host_ports: PortSet,
        expected_client_ports: list[PortSet],
    ) -> None:
        """Test start_port is correctly incremented in host and client ports.

        The start_port interface is specific to the AI Arena ladder manager interface.
        Only ladder managers which implement the start_port contiguous port reservation
        can utilize this interface.

        """
        port_config = MatchPortConfig(start_port)
        assert port_config.host_ports == expected_host_ports
        assert port_config.client_ports == expected_client_ports

    def test_default(self) -> None:
        """Test host and client ports have been selected."""
        port_config = MatchPortConfig()
        assert isinstance(port_config.host_ports, PortSet)
        assert isinstance(port_config.client_ports, list)
        assert len(port_config.client_ports) == 1
        assert isinstance(port_config.client_ports[0], PortSet)

        # Verify that the ports are distinct.
        # Here we assume that the ports portpicker has selected are in fact unused,
        # but we can still do a check to see that it's not incidentally picking
        # the same port twice.
        ports = [
            port_config.host_ports.game_port,
            port_config.host_ports.base_port,
            port_config.client_ports[0].game_port,
            port_config.client_ports[0].base_port,
        ]
        assert len(ports) == len(set(ports))
