from __future__ import annotations
from typing import Any
from framework.config.config_manager import ConfigManager


def build_device_running_config_request(
    config: ConfigManager,
    overrides: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Build the small live request payload used by the running-config slice."""
    device = config.get_primary_device(config.load_lab_topology())
    request = {
        "host": device["name"],
        "management_ip": device["management_ip"],
        "platform": config.device_platform,
        "transport": config.device_transport,
    }
    if overrides:
        request.update(overrides)
    return request
