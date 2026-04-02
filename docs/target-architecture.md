# Target Architecture

## Goal

Build a Python-based network security automation framework that validates a zero-trust lab through two coordinated paths:

- live validation against running devices
- offline validation against intended configs and topology

## Repository Shape

```text
network-security-automation-framework/
|-- docs/
|-- src/
|   |-- framework/
|   |   |-- config/
|   |   |-- inventory/
|   |   |-- logging/
|   |   |-- reporting/
|   |   |-- execution/
|   |   |   |-- live/
|   |   |   `-- offline/
|   |   `-- models/
|   `-- services/
|       |-- hardening/
|       |-- segmentation/
|       |-- routing/
|       `-- compliance/
|-- tests/
|   |-- live_tests/
|   |-- offline_tests/
|   |-- integration_tests/
|   `-- suite_tests/
|-- labs/
|   |-- intended/
|   `-- snapshots/
|-- conftest.py
`-- README.md
```

## Core Layers

### Config Manager

Responsibilities:

- load environment and runtime settings
- resolve active execution profile
- expose reporting, retry, timeout, and topology paths
- keep secrets and lab-specific values externalized

### Inventory Loading

Responsibilities:

- load device inventory for live execution
- load intended node/edge data for offline execution
- normalize common identifiers across both paths

### Live Device Execution Layer

Primary libraries:

- Nornir
- Scrapli
- Tenacity

Responsibilities:

- run commands or structured retrieval against devices
- normalize raw command outputs into parser-ready evidence
- centralize retry, timeout, and connection diagnostics

### Offline Batfish Execution Layer

Primary library:

- PyBatfish

Responsibilities:

- load snapshots of configs and topology
- answer policy and reachability questions offline
- normalize Batfish results into validator-ready evidence

## Service Layer Design

Each validation domain keeps the same service-oriented split.

### `*_service.py`

- test-facing orchestration
- coordinates request building, execution, and validation
- returns structured validation results

### `*_service_api.py`

- thin execution-facing adapter for the domain
- calls live or offline backend modules
- stays transport/runtime focused

### `*_service_request.py`

- shapes request objects and filter criteria
- keeps scenario inputs separate from execution details

## Validator Domains

### Hardening

Focus:

- management plane SSH-only posture
- disallowed plaintext management protocols
- control-plane access restrictions
- AAA and secure management expectations

### Segmentation

Focus:

- approved east-west reachability
- forbidden zone-to-zone access
- management network isolation
- expected path constraints between segments

### Routing

Focus:

- route presence and absence
- next-hop correctness
- path preference consistency
- route leak detection

### Drift / Compliance

Focus:

- intended vs observed state mismatch
- missing controls
- unauthorized config differences
- policy compliance summary

## Test Taxonomy

### `tests/live_tests`

Validates observed device state through live execution.

### `tests/offline_tests`

Validates intended topology, configs, and policy offline through Batfish.

### `tests/integration_tests`

Correlates both paths to prove the intended policy and live state align for the same scenario.

### `tests/suite_tests`

Owns broader orchestration, smoke selection, and curated lab suites.

## Deliberate Design Choice

Validators should operate on normalized evidence models. The evidence source may differ, but the assertion language should remain consistent. That keeps the framework modular and makes hybrid execution practical.
