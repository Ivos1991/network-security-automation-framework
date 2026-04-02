from __future__ import annotations

from typing import Any

from framework.config.config_manager import ConfigManager

try:
    from pybatfish.client.session import Session
    from pybatfish.datamodel.flow import HeaderConstraints
except ImportError:  # pragma: no cover - handled explicitly at runtime
    Session = None
    HeaderConstraints = None


class MockBatfishClient:
    """Fallback offline backend for scenarios not yet wired to a real Batfish query."""

    def __init__(self, config: ConfigManager) -> None:
        self._topology = config.load_lab_topology()

    def evaluate_expectation(self, expectation: dict[str, Any]) -> dict[str, Any]:
        """Evaluate one segmentation expectation against the lab policy map."""
        policy_map = {
            (policy["source"], policy["destination"]): policy["action"]
            for policy in self._topology.get("policies", [])
        }
        actual_action = policy_map.get(
            (expectation["source"], expectation["destination"]),
            "deny",
        )
        return {
            "source": expectation["source"],
            "destination": expectation["destination"],
            "expected_action": expectation["expected_action"],
            "action": actual_action,
            "allowed": actual_action == "allow",
            "denied": actual_action == "deny",
            "backend": "mock_batfish",
        }


class RealBatfishClient:
    """Minimal real Batfish adapter for the narrow offline segmentation slice."""

    _session: Session | None = None
    _initialized_snapshots: set[tuple[str, str]] = set()

    def __init__(self, config: ConfigManager) -> None:
        self._config = config

    def evaluate_expectation(
        self,
        request: dict[str, Any],
        expectation: dict[str, Any],
    ) -> dict[str, Any]:
        """Execute one Batfish `testFilters` question and normalize the answer."""
        batfish_query = expectation["batfish_query"]
        session = self._get_session()
        self._ensure_snapshot(session, request)
        headers = HeaderConstraints(
            srcIps=batfish_query["src_ip"],
            dstIps=batfish_query["dst_ip"],
        )
        answer_frame = (
            session.q.testFilters(
                nodes=batfish_query["node"],
                filters=batfish_query["filter_name"],
                headers=headers,
                startLocation=batfish_query["start_location"],
            )
            .answer(snapshot=request["snapshot_name"])
            .frame()
        )
        if answer_frame.empty:
            raise RuntimeError(
                "Batfish returned no filter evaluation rows for the configured segmentation scenario."
            )

        first_row = answer_frame.iloc[0].to_dict()
        actual_action = self._normalize_batfish_action(first_row.get("Action"))
        if actual_action not in {"allow", "deny"}:
            raise RuntimeError(f"Unsupported Batfish action value: {first_row.get('Action')!r}")

        return {
            "source": expectation["source"],
            "destination": expectation["destination"],
            "expected_action": expectation["expected_action"],
            "action": actual_action,
            "allowed": actual_action == "allow",
            "denied": actual_action == "deny",
            "backend": "real_batfish",
            "batfish_evidence": {
                "snapshot_name": request["snapshot_name"],
                "node": batfish_query["node"],
                "filter_name": batfish_query["filter_name"],
                "start_location": batfish_query["start_location"],
                "src_ip": batfish_query["src_ip"],
                "dst_ip": batfish_query["dst_ip"],
                "action": actual_action,
                "line_content": str(first_row.get("Line_Content", "")),
                "trace": str(first_row.get("Trace", "")),
            },
        }

    def _get_session(self) -> Session:
        """Create or reuse the shared Batfish session for the active network."""
        if Session is None or HeaderConstraints is None:
            raise RuntimeError(
                "PyBatfish is not installed. Install project requirements before running offline Batfish validation."
            )

        if self.__class__._session is None:
            self.__class__._session = Session(host=self._config.batfish_host)
        self.__class__._session.set_network(self._config.batfish_network)
        return self.__class__._session

    def _ensure_snapshot(self, session: Session, request: dict[str, Any]) -> None:
        """Initialize the configured snapshot once and reuse it across test runs."""
        snapshot_key = (self._config.batfish_network, request["snapshot_name"])
        if snapshot_key not in self.__class__._initialized_snapshots:
            session.init_snapshot(
                request["snapshot_path"],
                name=request["snapshot_name"],
                overwrite=True,
            )
            self.__class__._initialized_snapshots.add(snapshot_key)
        session.set_snapshot(request["snapshot_name"])

    @staticmethod
    def _normalize_batfish_action(action: object) -> str:
        """Map Batfish action values to the repository's normalized allow/deny contract."""
        normalized_action = str(action).strip().lower()
        if normalized_action == "permit":
            return "allow"
        if normalized_action == "deny":
            return "deny"
        return normalized_action


class PolicyServiceApi:
    """Thin runtime-facing adapter for offline policy execution."""

    def __init__(self, config: ConfigManager) -> None:
        self._mock_client = MockBatfishClient(config)
        self._real_client = RealBatfishClient(config)

    def evaluate_segmentation(self, request: dict[str, Any]) -> dict[str, Any]:
        """Evaluate each expectation with the real or mock backend and normalize the result."""
        evaluations = []
        batfish_question_summary = []
        for expectation in request["expectations"]:
            if expectation.get("batfish_query"):
                evaluation = self._real_client.evaluate_expectation(request, expectation)
                batfish_question_summary.append(evaluation["batfish_evidence"])
            else:
                evaluation = self._mock_client.evaluate_expectation(expectation)
            evaluations.append(evaluation)

        return {
            "snapshot_name": request["snapshot_name"],
            "evaluations": evaluations,
            "backend": self._summarize_backend(evaluations),
            "batfish_question_summary": batfish_question_summary,
        }

    @staticmethod
    def _summarize_backend(evaluations: list[dict[str, Any]]) -> str:
        """Collapse per-evaluation backends into a compact run-level label."""
        backend_names = {evaluation["backend"] for evaluation in evaluations}
        if backend_names == {"real_batfish"}:
            return "real_batfish"
        if backend_names == {"mock_batfish"}:
            return "mock_batfish"
        return "mixed_offline_backends"
