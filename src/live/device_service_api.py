from __future__ import annotations

from typing import Any

from framework.config.config_manager import ConfigManager


class MockScrapliClient:
    """Mock live backend that returns deterministic running-config evidence."""

    def __init__(self, config: ConfigManager) -> None:
        self._config = config

    def get_running_config(self, request: dict[str, Any]) -> dict[str, Any]:
        """Return a normalized running-config response without real device access."""
        return {
            "host": request["host"],
            "management_ip": request["management_ip"],
            "platform": request["platform"],
            "command": "show running-config",
            "output": request.get("running_config_override", self._config.device_running_config),
            "backend": "mock_scrapli",
        }


class DeviceServiceApi:
    """Thin runtime-facing adapter for the live device service."""

    def __init__(self, config: ConfigManager) -> None:
        self._client = MockScrapliClient(config)

    def get_device_running_config(self, request: dict[str, Any]) -> dict[str, Any]:
        """Delegate running-config retrieval to the configured backend."""
        return self._client.get_running_config(request)
