from __future__ import annotations
from typing import Any
from framework.config.config_manager import ConfigManager
from offline.policy_service_api import PolicyServiceApi
from offline.policy_service_request import build_segmentation_policy_request
from validators.segmentation.network_segmentation_validator import validate_segmentation_policy


def validate_segmentation(
    config: ConfigManager,
    source: str | None = None,
    destination: str | None = None,
) -> dict[str, Any]:
    """Run the offline segmentation slice and return normalized reachability evidence."""
    request = build_segmentation_policy_request(config=config, source=source, destination=destination)
    api = PolicyServiceApi(config)
    reachability_result = api.evaluate_segmentation(request)
    validation = validate_segmentation_policy(reachability_result)
    return {
        "request": request,
        "runtime_result": reachability_result,
        "validation": validation,
    }
