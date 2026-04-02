from __future__ import annotations
from collections.abc import Sequence
from copy import deepcopy
from typing import Any
from framework.config.config_manager import ConfigManager
from framework.models.compliance_status import (
    HybridComplianceAggregation,
    HybridComplianceStatus,
)
from live.device_service import validate_device_hardening
from offline.policy_service import validate_segmentation
from validators.compliance.hybrid_access_compliance_validator import (
    validate_hybrid_access_compliance,
)
from validators.compliance.management_plane_compliance_validator import (
    validate_management_plane_compliance,
)


def validate_management_plane_compliance_slice(config: ConfigManager) -> dict[str, Any]:
    """Compare intended and observed management-plane posture for the current lab device."""
    topology = config.load_lab_topology()
    live_result = validate_device_hardening(config)
    intended_posture = config.get_intended_management_plane_posture(topology)
    observed_posture = live_result["observed_posture"]
    validation = validate_management_plane_compliance(intended_posture, observed_posture)

    return {
        "device": config.get_primary_device(topology)["name"],
        "intended_posture": intended_posture,
        "observed_posture": observed_posture,
        "validation": validation,
    }


def validate_hybrid_access_compliance_slice(
    config: ConfigManager,
    offline_action_override: str | None = None,
    live_running_config_override: str | None = None,
) -> dict[str, Any]:
    """Correlate one intended access rule with offline policy and live hardening signals."""
    topology = config.load_lab_topology()
    intended_policy = config.get_intended_access_rule(topology)
    offline_result = validate_segmentation(
        config,
        source=intended_policy["source"],
        destination=intended_policy["destination"],
    )
    live_overrides = None
    if live_running_config_override is not None:
        live_overrides = {"running_config_override": live_running_config_override}
    live_result = validate_device_hardening(config, overrides=live_overrides)
    offline_evaluation = deepcopy(offline_result["runtime_result"]["evaluations"][0])
    if offline_action_override is not None:
        offline_evaluation["action"] = offline_action_override
        offline_evaluation["allowed"] = offline_action_override == "allow"
        offline_evaluation["denied"] = offline_action_override == "deny"

    live_signal = {
        "ssh_enabled": live_result["observed_posture"]["ssh_enabled"],
        "telnet_enabled": live_result["observed_posture"]["telnet_enabled"],
        "banner_login_present": live_result["observed_posture"]["banner_login_present"],
    }
    validation = validate_hybrid_access_compliance(
        intended_policy=intended_policy,
        offline_evaluation=offline_evaluation,
        live_signal=live_signal,
    )
    compliance_status = build_hybrid_compliance_status(
        intended_policy=intended_policy,
        offline_evaluation=offline_evaluation,
        live_signal=live_signal,
        validation=validation,
    )

    return {
        "intended_policy": intended_policy,
        "offline_evaluation": offline_evaluation,
        "live_signal": live_signal,
        "offline_action_override": offline_action_override,
        "live_running_config_override": live_running_config_override,
        "validation": validation,
        "compliance_status": compliance_status.model_dump(),
    }


def build_hybrid_compliance_status(
    intended_policy: dict[str, str],
    offline_evaluation: dict[str, object],
    live_signal: dict[str, bool],
    validation: dict[str, Any],
) -> HybridComplianceStatus:
    """Convert hybrid validation output into the normalized compliance contract."""
    mismatch_type = "none"
    if not validation["offline_policy_matches"]:
        mismatch_type = "offline_policy_mismatch"
    elif not validation["live_management_ready"]:
        mismatch_type = "live_posture_mismatch"

    overall_status = "pass" if validation["passed"] else "fail"
    return HybridComplianceStatus(
        overall_status=overall_status,
        mismatch_type=mismatch_type,
        intended_policy=intended_policy,
        offline_result=offline_evaluation,
        live_posture_status=live_signal,
        mismatch_reason=validation["mismatch_reason"],
        summary=validation["summary"],
    )


def aggregate_hybrid_compliance_statuses(
    statuses: Sequence[HybridComplianceStatus],
) -> HybridComplianceAggregation:
    """Summarize a small set of hybrid compliance outcomes for reporting."""
    mismatch_type_counts = {
        "none": 0,
        "offline_policy_mismatch": 0,
        "live_posture_mismatch": 0,
    }

    passed_results = 0
    for status in statuses:
        if status.overall_status == "pass":
            passed_results += 1
        mismatch_type_counts[status.mismatch_type] += 1

    total_results = len(statuses)
    failed_results = total_results - passed_results
    summary = (
        f"{total_results} hybrid results: "
        f"{passed_results} passed, {failed_results} failed; "
        "mismatch types: "
        f"none={mismatch_type_counts['none']}, "
        f"offline_policy_mismatch={mismatch_type_counts['offline_policy_mismatch']}, "
        f"live_posture_mismatch={mismatch_type_counts['live_posture_mismatch']}"
    )

    return HybridComplianceAggregation(
        total_results=total_results,
        passed_results=passed_results,
        failed_results=failed_results,
        mismatch_type_counts=mismatch_type_counts,
        summary=summary,
    )
