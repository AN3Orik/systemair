"""Tests for Modbus connection and worker recovery."""

# ruff: noqa: PT009

from __future__ import annotations

import asyncio
import contextlib
import unittest
from types import SimpleNamespace
from unittest.mock import AsyncMock, patch

from pymodbus.exceptions import ModbusIOException

from custom_components.systemair.api import SystemairModbusClient


class FakeModbusTransport:
    """Minimal Modbus transport with controlled read behavior."""

    def __init__(self, read_result: object) -> None:
        """Store the result or exception returned by the next read."""
        self.connected = True
        self.closed = False
        self._read_result = read_result

    async def connect(self) -> bool:
        """Mark the fake transport as connected."""
        self.connected = True
        return True

    async def read_holding_registers(self, **_kwargs: int) -> object:
        """Return or raise the configured read result."""
        if isinstance(self._read_result, Exception):
            raise self._read_result
        return self._read_result

    def close(self) -> None:
        """Mark the fake transport as closed."""
        self.connected = False
        self.closed = True


class ModbusRecoveryTest(unittest.IsolatedAsyncioTestCase):
    """Verify transient transport errors cannot permanently stop Modbus I/O."""

    async def test_modbus_io_error_closes_socket_and_retries(self) -> None:
        """A pymodbus no-response error reconnects before retrying the request."""
        client = SystemairModbusClient(host="127.0.0.1", port=502, slave_id=1)
        failed_transport = FakeModbusTransport(ModbusIOException("No response received"))
        recovered_transport = FakeModbusTransport(SimpleNamespace(registers=[230], isError=lambda: False))
        client._client = failed_transport  # noqa: SLF001

        with (
            patch("custom_components.systemair.api.AsyncModbusTcpClient", return_value=recovered_transport),
            patch("custom_components.systemair.api.asyncio.sleep", AsyncMock()),
        ):
            try:
                result = await client._execute_request("read", address=2000, count=1)  # noqa: SLF001
            except ModbusIOException:
                self.fail("ModbusIOException escaped instead of triggering reconnect")

        self.assertEqual(result, [230])
        self.assertTrue(failed_transport.closed)
        self.assertIs(client._client, recovered_transport)  # noqa: SLF001

    async def test_worker_continues_after_unexpected_request_error(self) -> None:
        """One failed request cannot leave every subsequent command queued forever."""
        client = SystemairModbusClient(host="127.0.0.1", port=502, slave_id=1)
        results: list[Exception | list[int]] = [RuntimeError("request failed"), [230]]

        async def execute_request(_request_type: str, _address: int, **_kwargs: int) -> list[int]:
            next_result = results.pop(0)
            if isinstance(next_result, Exception):
                raise next_result
            return next_result

        client._execute_request = execute_request  # type: ignore[method-assign]  # noqa: SLF001
        client._is_running = True  # noqa: SLF001
        worker_task = asyncio.create_task(client._modbus_worker())  # noqa: SLF001

        try:
            try:
                await asyncio.wait_for(client._queue_request("read", address=1000), timeout=0.1)  # noqa: SLF001
            except RuntimeError:
                pass
            except TimeoutError:
                self.fail("Modbus worker stopped without completing the failed request")

            result = await asyncio.wait_for(client._queue_request("read", address=2000), timeout=0.1)  # noqa: SLF001

            self.assertEqual(result, [230])
            self.assertFalse(worker_task.done())
        finally:
            client._is_running = False  # noqa: SLF001
            worker_task.cancel()
            with contextlib.suppress(asyncio.CancelledError, RuntimeError):
                await worker_task
