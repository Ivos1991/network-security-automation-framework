from __future__ import annotations
import os
from functools import lru_cache
from ipaddress import ip_network
from pathlib import Path
from typing import Any
import yaml
from pydantic import BaseModel, Field


class ConfigManager(BaseModel):
    """Centralized runtime configuration for the lab, live path, and offline path."""

    framework_env: str = Field(default="local")
    execution_mode: str = Field(default="hybrid")
    lab_topology_path: str = Field(default="labs/current_lab.yaml")
    device_host: str = Field(default="lab-edge-01")
    device_platform: str = Field(default="cisco_iosxe")
    device_transport: str = Field(default="system")
    device_auth_username: str = Field(default="lab-user")
    device_auth_password: str = Field(default="change-me")
    device_running_config: str = Field(
        default=(
            "hostname lab-edge-01\n"
            "banner login Authorized Access Only\n"
            "service password-encryption\n"
            "ip ssh version 2\n"
            "line vty 0 4\n"
            " transport input ssh\n"
        )
    )
    offline_snapshot_name: str = Field(default="zero_trust_lab")
    offline_snapshot_path: str = Field(default="labs/snapshots/zero_trust_lab")
    batfish_host: str = Field(default="localhost")
    batfish_network: str = Field(default="zero_trust_lab")
    segmentation_source: str = Field(default="user_subnet")
    segmentation_destination: str = Field(default="restricted_subnet")
    segmentation_expected_action: str = Field(default="deny")
    segmentation_secondary_source: str = Field(default="admin_subnet")
    segmentation_secondary_destination: str = Field(default="restricted_subnet")
    segmentation_secondary_expected_action: str = Field(default="allow")

    @classmethod
    @lru_cache(maxsize=1)
    def from_env(cls) -> "ConfigManager":
        """Create a cached configuration object from environment variables."""
        return cls(
            framework_env=os.getenv("FRAMEWORK_ENV", "local"),
            execution_mode=os.getenv("EXECUTION_MODE", "hybrid"),
            lab_topology_path=os.getenv("LAB_TOPOLOGY_PATH", "labs/current_lab.yaml"),
            device_host=os.getenv("DEVICE_HOST", "lab-edge-01"),
            device_platform=os.getenv("DEVICE_PLATFORM", "cisco_iosxe"),
            device_transport=os.getenv("DEVICE_TRANSPORT", "system"),
            device_auth_username=os.getenv("DEVICE_AUTH_USERNAME", "lab-user"),
            device_auth_password=os.getenv("DEVICE_AUTH_PASSWORD", "change-me"),
            device_running_config=os.getenv(
                "DEVICE_RUNNING_CONFIG",
                (
                    "hostname lab-edge-01\n"
                    "banner login Authorized Access Only\n"
                    "service password-encryption\n"
                    "ip ssh version 2\n"
                    "line vty 0 4\n"
                    " transport input ssh\n"
                ),
            ),
            offline_snapshot_name=os.getenv("OFFLINE_SNAPSHOT_NAME", "zero_trust_lab"),
            offline_snapshot_path=os.getenv(
                "OFFLINE_SNAPSHOT_PATH",
                "labs/snapshots/zero_trust_lab",
            ),
            batfish_host=os.getenv("BATFISH_HOST", "localhost"),
            batfish_network=os.getenv("BATFISH_NETWORK", "zero_trust_lab"),
            segmentation_source=os.getenv("SEGMENTATION_SOURCE", "user_subnet"),
            segmentation_destination=os.getenv("SEGMENTATION_DESTINATION", "restricted_subnet"),
            segmentation_expected_action=os.getenv("SEGMENTATION_EXPECTED_ACTION", "deny"),
            segmentation_secondary_source=os.getenv("SEGMENTATION_SECONDARY_SOURCE", "admin_subnet"),
            segmentation_secondary_destination=os.getenv(
                "SEGMENTATION_SECONDARY_DESTINATION",
                "restricted_subnet",
            ),
            segmentation_secondary_expected_action=os.getenv(
                "SEGMENTATION_SECONDARY_EXPECTED_ACTION",
                "allow",
            ),
        )

    def load_lab_topology(self) -> dict[str, Any]:
        """Load the active shared lab asset from disk."""
        topology_path = self._resolve_repo_root() / self.lab_topology_path
        with topology_path.open("r", encoding="utf-8") as handle:
            return yaml.safe_load(handle)

    def get_primary_device(self, topology: dict[str, Any]) -> dict[str, Any]:
        """Return the single device used by the current narrow live slice."""
        return topology["devices"][0]

    def get_intended_management_plane_posture(self, topology: dict[str, Any]) -> dict[str, bool]:
        """Expose the intended management-plane posture for compliance comparison."""
        device = self.get_primary_device(topology)
        return device["intended_management_plane"]

    def get_segmentation_expectations(
        self,
        topology: dict[str, Any],
        source: str | None = None,
        destination: str | None = None,
    ) -> list[dict[str, str]]:
        """Resolve the small set of segmentation expectations used by the offline slice."""
        policies = topology.get("policies", [])
        if source and destination:
            for policy in policies:
                if policy["source"] == source and policy["destination"] == destination:
                    return [
                        {
                            "source": source,
                            "destination": destination,
                            "expected_action": policy["action"],
                        }
                    ]
            return []

        expected_pairs = {
            (self.segmentation_source, self.segmentation_destination): self.segmentation_expected_action,
            (self.segmentation_secondary_source, self.segmentation_secondary_destination): (
                self.segmentation_secondary_expected_action
            ),
        }
        expectations: list[dict[str, str]] = []
        for policy in policies:
            policy_key = (policy["source"], policy["destination"])
            if policy_key in expected_pairs:
                expectations.append(
                    {
                        "source": policy["source"],
                        "destination": policy["destination"],
                        "expected_action": expected_pairs[policy_key],
                    }
                )
        return expectations

    def get_intended_access_rule(self, topology: dict[str, Any]) -> dict[str, str]:
        """Return the intended access rule used by the hybrid compliance slice."""
        return topology["intended_access_rules"][0]

    def get_batfish_snapshot_path(self) -> str:
        """Resolve the absolute path to the active Batfish snapshot."""
        return str(self._resolve_repo_root() / self.offline_snapshot_path)

    def get_batfish_segmentation_scenario(
        self,
        topology: dict[str, Any],
        source: str,
        destination: str,
    ) -> dict[str, str] | None:
        """Return Batfish query metadata for a supported segmentation scenario, if defined."""
        offline_batfish = topology.get("offline_batfish", {})
        for scenario in offline_batfish.get("segmentation_scenarios", []):
            if scenario["source"] == source and scenario["destination"] == destination:
                return {
                    "node": scenario["node"],
                    "filter_name": scenario["filter_name"],
                    "start_location": scenario["start_location"],
                    "src_ip": scenario.get("src_ip", self._get_default_host_ip(topology, source)),
                    "dst_ip": scenario.get("dst_ip", self._get_default_host_ip(topology, destination)),
                }
        return None

    def _get_default_host_ip(self, topology: dict[str, Any], segment_name: str) -> str:
        """Pick a deterministic host IP from a segment CIDR for Batfish filter evaluation."""
        segment_cidr = topology["segments"][segment_name]
        return str(next(ip_network(segment_cidr).hosts()))

    @staticmethod
    def _resolve_repo_root() -> Path:
        """Resolve the repository root from the current module location."""
        return Path(__file__).resolve().parents[3]
