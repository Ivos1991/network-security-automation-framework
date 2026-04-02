from __future__ import annotations

from typing import Any

from framework.config.config_manager import ConfigManager


def build_segmentation_policy_request(
    config: ConfigManager,
    source: str | None = None,
    destination: str | None = None,
) -> dict[str, Any]:
    """Build the offline segmentation request with optional Batfish query metadata."""
    topology = config.load_lab_topology()
    expectations = config.get_segmentation_expectations(
        topology,
        source=source,
        destination=destination,
    )
    enriched_expectations = []
    for expectation in expectations:
        enriched_expectations.append(
            {
                **expectation,
                "batfish_query": config.get_batfish_segmentation_scenario(
                    topology,
                    source=expectation["source"],
                    destination=expectation["destination"],
                ),
            }
        )
    return {
        "snapshot_name": config.offline_snapshot_name,
        "snapshot_path": config.get_batfish_snapshot_path(),
        "expectations": enriched_expectations,
    }
