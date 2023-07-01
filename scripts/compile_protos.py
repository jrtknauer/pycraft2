"""Compile Python protocol buffer API from s2client-proto."""

import logging
import os
import subprocess
import sys
from distutils.spawn import find_executable
from pathlib import Path
from typing import Iterator

import click

LOGGER = logging.getLogger(__name__)


def check_protoc() -> None:
    """Validate protoc installation."""
    protoc = find_executable("protoc")
    assert protoc

    # If more than one protoc is on the path.
    assert os.pathsep not in protoc


def check_mypy_protobuf() -> None:
    """Validate mypy-protobuf installation."""
    mypy_protobuf = find_executable("protoc-gen-mypy")
    assert mypy_protobuf

    LOGGER.info("Confirmed protoc-gen-mypy installed.")


def proto_files(root: Path) -> Iterator[str]:
    """Yields the absolute path of all .proto files under root."""
    return (
        os.path.join(dirpath, filename)
        for dirpath, _, filenames in os.walk(str(root))
        for filename in filenames
        if filename.endswith(".proto")
    )


def compile_proto(include: Path, out: Path, proto: str) -> None:
    """Compile Python protocol buffer API with stubs."""
    LOGGER.info(f"Compiling {proto}")
    protoc_command = (
        "protoc",
        "--mypy_out",
        out,
        "--proto_path",
        include,
        "--python_out",
        out,
        proto,
    )
    if subprocess.call(protoc_command) != 0:
        LOGGER.error("Incompatible protoc version.")
        sys.exit()


@click.command()
@click.option(
    "--proto",
    default="/home/jrtknauer/jrt/pycraft2/s2client-proto",
    help="Path to sc2client-proto directory.",
)
@click.option(
    "--python_out",
    default="/home/jrtknauer/jrt/pycraft2/pycraft2",
    help="Output directory for compiled protos.",
)
def cli(proto: str, python_out: str) -> None:
    """"""
    check_protoc()
    check_mypy_protobuf()

    include = Path(proto)
    out = Path(python_out)

    for proto in proto_files(include):
        compile_proto(include=include, out=out, proto=proto)


if __name__ == "__main__":
    """"""
    logging.basicConfig(level=logging.INFO)
    cli()
