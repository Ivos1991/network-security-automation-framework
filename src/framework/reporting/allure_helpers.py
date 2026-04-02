from __future__ import annotations

import json
from typing import Any

import allure


def attach_text(name: str, content: str) -> None:
    """Attach plain text evidence to Allure."""
    allure.attach(content, name=name, attachment_type=allure.attachment_type.TEXT)


def attach_json(name: str, content: dict[str, Any]) -> None:
    """Attach JSON-serializable evidence to Allure in a stable, readable format."""
    allure.attach(
        json.dumps(content, indent=2, sort_keys=True),
        name=name,
        attachment_type=allure.attachment_type.JSON,
    )


def attach_inventory_context(lab_topology: dict[str, Any]) -> None:
    """Attach the shared lab topology used to derive the current scenario."""
    attach_json("inventory-topology-context", lab_topology)


def attach_live_evidence(result: dict[str, Any]) -> None:
    """Attach compact live-path evidence for the current hardening check."""
    attach_json("live-request-context", result["request"])
    attach_text("live-running-config", result["runtime_result"]["output"])
    attach_json("live-validation-summary", result["validation"])


def attach_offline_evidence(result: dict[str, Any]) -> None:
    """Attach compact offline-path evidence, including Batfish details when present."""
    attach_json("offline-request-context", result["request"])
    attach_json("offline-reachability-result", result["runtime_result"])
    if result["runtime_result"].get("batfish_question_summary"):
        attach_json(
            "offline-batfish-summary",
            {
                "snapshot_name": result["runtime_result"]["snapshot_name"],
                "backend": result["runtime_result"]["backend"],
                "questions": result["runtime_result"]["batfish_question_summary"],
            },
        )
    attach_json("offline-validation-summary", result["validation"])


def attach_validation_summary(name: str, content: dict[str, Any]) -> None:
    """Attach a concise validation summary payload under a caller-defined name."""
    attach_json(name, content)


def attach_compliance_evidence(result: dict[str, Any]) -> None:
    """Attach intended versus observed management-plane evidence."""
    attach_json("intended-management-plane-posture", result["intended_posture"])
    attach_json("observed-management-plane-posture", result["observed_posture"])
    attach_json("management-plane-compliance-summary", result["validation"])


def attach_hybrid_evidence(result: dict[str, Any]) -> None:
    """Attach normalized hybrid compliance evidence and mismatch detail when needed."""
    attach_json("hybrid-compliance-status", result["compliance_status"])
    if result["compliance_status"]["overall_status"] == "fail":
        attach_json(
            "hybrid-mismatch-summary",
            {
                "overall_status": result["compliance_status"]["overall_status"],
                "mismatch_type": result["compliance_status"]["mismatch_type"],
                "intended_policy": result["compliance_status"]["intended_policy"],
                "offline_result": result["compliance_status"]["offline_result"],
                "live_posture": result["compliance_status"]["live_posture_status"],
                "mismatch_reason": result["compliance_status"]["mismatch_reason"],
            },
        )


def attach_hybrid_aggregation_summary(result: dict[str, Any]) -> None:
    """Attach suite-level hybrid aggregation evidence."""
    attach_json("hybrid-compliance-aggregation", result)
