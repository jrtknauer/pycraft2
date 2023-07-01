"""Test the pycraft.util module."""

from pycraft2.util import unused_port_generator


class TestUnusedPortGenerator:
    """Test the unused_port_generator module function."""

    def test_unused_port_generator(self):
        """Test the ports are distinct.

        Do not verify if the ports are actually unused, just that portpicker is not
        incidentally picking the same port twice as a sanity check. Use 4 ports as that
        is the maximum number of ports required by pycraft2.

        """
        ports = [next(unused_port_generator()) for _ in range(4)]
        assert len(ports) == len(set(ports))
