from __future__ import annotations
from typing import Literal
from pydantic import BaseModel


class HybridComplianceStatus(BaseModel):
    """Normalized hybrid compliance result shared across validation and reporting layers."""

    overall_status: Literal["pass", "fail"]
    mismatch_type: Literal["none", "offline_policy_mismatch", "live_posture_mismatch"]
    intended_policy: dict[str, str]
    offline_result: dict[str, object]
    live_posture_status: dict[str, bool]
    mismatch_reason: str
    summary: str


class HybridComplianceAggregation(BaseModel):
    """Compact aggregation of multiple hybrid compliance outcomes for suite reporting."""

    total_results: int
    passed_results: int
    failed_results: int
    mismatch_type_counts: dict[
        Literal["none", "offline_policy_mismatch", "live_posture_mismatch"], int
    ]
    summary: str | None = None
