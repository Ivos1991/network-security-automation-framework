from __future__ import annotations
import os
import subprocess
import time
from typing import Any
from urllib.error import HTTPError, URLError
from urllib.request import urlopen
import pytest
from framework.config.config_manager import ConfigManager
from framework.models.compliance_status import HybridComplianceStatus
from integration.compliance_service import (
    aggregate_hybrid_compliance_statuses,
    validate_hybrid_access_compliance_slice,
    validate_management_plane_compliance_slice,
)
from live.device_service import validate_device_hardening
from offline.policy_service import validate_segmentation


@pytest.fixture(scope="session")
def config() -> ConfigManager:
    """Load the shared framework configuration once per test session."""
    return ConfigManager.from_env()


@pytest.fixture(scope="session")
def lab_topology(config: ConfigManager) -> dict[str, Any]:
    """Expose the shared lab asset to tests that attach context or derive expectations."""
    return config.load_lab_topology()


@pytest.fixture(scope="session")
def live_negative_running_config_override() -> str:
    """Provide the deterministic insecure live config used by the hybrid negative case."""
    return (
        "hostname lab-edge-01\n"
        "banner login Authorized Access Only\n"
        "service password-encryption\n"
        "ip ssh version 2\n"
        "line vty 0 4\n"
        " transport input ssh telnet\n"
    )


@pytest.fixture(scope="session")
def batfish_service(config: ConfigManager) -> dict[str, str]:
    """Ensure the local Batfish service is available for real offline validation."""
    container_name = "network-security-batfish"
    image_name = "batfish/allinone"

    running_container = subprocess.run(
        [
            "docker",
            "ps",
            "--filter",
            f"name={container_name}",
            "--format",
            "{{.Names}}",
        ],
        check=True,
        capture_output=True,
        text=True,
    )
    if container_name not in running_container.stdout.splitlines():
        existing_container = subprocess.run(
            [
                "docker",
                "ps",
                "-a",
                "--filter",
                f"name={container_name}",
                "--format",
                "{{.Names}}",
            ],
            check=True,
            capture_output=True,
            text=True,
        )
        if container_name in existing_container.stdout.splitlines():
            subprocess.run(["docker", "start", container_name], check=True, capture_output=True, text=True)
        else:
            subprocess.run(
                [
                    "docker",
                    "run",
                    "-d",
                    "--name",
                    container_name,
                    "-p",
                    "8888:8888",
                    "-p",
                    "9996:9996",
                    image_name,
                ],
                check=True,
                capture_output=True,
                text=True,
            )

    deadline = time.time() + 120
    last_error = ""
    while time.time() < deadline:
        try:
            with urlopen("http://localhost:9996", timeout=5) as response:
                if response.status < 500:
                    break
        except HTTPError as exc:
            if exc.code < 500:
                break
            last_error = str(exc)
        except ConnectionResetError as exc:
            last_error = str(exc)
        except URLError as exc:
            last_error = str(exc)
        except OSError as exc:
            last_error = str(exc)
        time.sleep(2)
    else:
        raise RuntimeError(f"Batfish service did not become ready in time. Last error: {last_error}")

    return {
        "container_name": container_name,
        "host": config.batfish_host,
        "network": config.batfish_network,
    }


@pytest.fixture(scope="session")
def live_validation_result(config: ConfigManager) -> dict[str, Any]:
    """Run the live hardening slice once for reuse across the small test suite."""
    return validate_device_hardening(config)


@pytest.fixture(scope="session")
def offline_validation_result(
    config: ConfigManager,
    batfish_service: dict[str, str],
) -> dict[str, Any]:
    """Run the offline segmentation slice once for reuse across offline and integration tests."""
    _ = batfish_service
    return validate_segmentation(config)


@pytest.fixture(scope="session")
def management_plane_compliance_result(config: ConfigManager) -> dict[str, Any]:
    """Run the management-plane compliance slice once for integration assertions."""
    return validate_management_plane_compliance_slice(config)


@pytest.fixture(scope="session")
def hybrid_validation_result(config: ConfigManager) -> dict[str, Any]:
    """Run the happy-path hybrid compliance slice once for integration assertions."""
    return validate_hybrid_access_compliance_slice(config)


@pytest.fixture(scope="session")
def hybrid_offline_mismatch_result(config: ConfigManager) -> dict[str, Any]:
    """Run the deterministic offline-side hybrid mismatch once for reuse in tests."""
    return validate_hybrid_access_compliance_slice(
        config,
        offline_action_override="deny",
    )


@pytest.fixture(scope="session")
def hybrid_live_mismatch_result(
    config: ConfigManager,
    live_negative_running_config_override: str,
) -> dict[str, Any]:
    """Run the deterministic live-side hybrid mismatch once for reuse in tests."""
    return validate_hybrid_access_compliance_slice(
        config,
        live_running_config_override=live_negative_running_config_override,
    )


@pytest.fixture(scope="session")
def hybrid_aggregation_result(
    hybrid_validation_result: dict[str, Any],
    hybrid_offline_mismatch_result: dict[str, Any],
    hybrid_live_mismatch_result: dict[str, Any],
) -> dict[str, Any]:
    """Build the suite-level hybrid aggregation payload once for reuse in tests."""
    aggregation = aggregate_hybrid_compliance_statuses(
        [
            HybridComplianceStatus.model_validate(hybrid_validation_result["compliance_status"]),
            HybridComplianceStatus.model_validate(hybrid_offline_mismatch_result["compliance_status"]),
            HybridComplianceStatus.model_validate(hybrid_live_mismatch_result["compliance_status"]),
        ]
    )
    return {
        "aggregation": aggregation,
        "statuses": [
            hybrid_validation_result["compliance_status"],
            hybrid_offline_mismatch_result["compliance_status"],
            hybrid_live_mismatch_result["compliance_status"],
        ],
    }


@pytest.fixture(scope="session")
def offline_user_to_restricted_evaluation(offline_validation_result: dict[str, Any]) -> dict[str, Any]:
    """Return the user-to-restricted offline evaluation for focused assertions."""
    return next(
        evaluation
        for evaluation in offline_validation_result["runtime_result"]["evaluations"]
        if evaluation["source"] == "user_subnet" and evaluation["destination"] == "restricted_subnet"
    )


@pytest.fixture(scope="session")
def offline_admin_to_restricted_evaluation(offline_validation_result: dict[str, Any]) -> dict[str, Any]:
    """Return the admin-to-restricted offline evaluation for focused assertions."""
    return next(
        evaluation
        for evaluation in offline_validation_result["runtime_result"]["evaluations"]
        if evaluation["source"] == "admin_subnet" and evaluation["destination"] == "restricted_subnet"
    )


def pytest_configure() -> None:
    """Keep subprocess output UTF-8 safe across local and CI runs."""
    os.environ.setdefault("PYTHONUTF8", "1")
