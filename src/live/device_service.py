from __future__ import annotations
from typing import Any
from framework.config.config_manager import ConfigManager
from live.device_service_api import DeviceServiceApi
from live.device_service_request import build_device_running_config_request
from validators.hardening.device_hardening_validator import (
    validate_device_hardening as validate_device_hardening_rules,
)


def get_device_running_config(
    config: ConfigManager,
    overrides: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Fetch the running config through the live service API layer."""
    request = build_device_running_config_request(config, overrides=overrides)
    api = DeviceServiceApi(config)
    return api.get_device_running_config(request)


def validate_device_hardening(
    config: ConfigManager,
    overrides: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Run the current hardening slice and return normalized evidence."""
    running_config_result = get_device_running_config(config, overrides=overrides)
    observed_posture = extract_observed_management_plane_posture(running_config_result["output"])
    validation = validate_device_hardening_output(running_config_result["output"])
    return {
        "request": build_device_running_config_request(config, overrides=overrides),
        "runtime_result": running_config_result,
        "observed_posture": observed_posture,
        "validation": validation,
    }


def validate_device_hardening_output(running_config: str) -> dict[str, Any]:
    """Apply the hardening validator to a running config string."""
    return validate_device_hardening_rules(running_config)


def extract_observed_management_plane_posture(running_config: str) -> dict[str, bool]:
    """Extract the small set of live management-plane signals used by the compliance slice."""
    normalized_config = running_config.lower()
    return {
        "ssh_enabled": "ssh" in normalized_config,
        "telnet_enabled": "telnet" in normalized_config,
        "banner_login_present": "banner login" in normalized_config,
    }
