"""Control test to verify pytest is functional."""

import asyncio

import pytest


def test_foo() -> None:
    """"""
    assert True


@pytest.mark.asyncio
async def test_async_foo() -> None:
    await asyncio.sleep(0.1)
    assert True
