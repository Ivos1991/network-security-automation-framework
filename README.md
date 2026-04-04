# Network Security Automation Framework

This repository demonstrates a cybersecurity-focused automation approach for validating a small zero-trust lab through two coordinated paths:

- a mocked live validation path for management-plane hardening
- a real Batfish-backed offline validation path for segmentation intent

The architecture is intentionally lean. It keeps the service/API/request split explicit, uses a shared lab asset to correlate both paths, and limits scope to a few deterministic scenarios that are credible for a portfolio repo.

## Project Summary

Implemented validation slices:

- live device hardening validation through a mocked Scrapli-style backend
- offline segmentation validation through real Batfish `testFilters` queries
- hybrid compliance correlation that compares intended policy, offline evaluation, and live posture
- compact suite-level aggregation for hybrid compliance reporting

Validated offline segmentation scenarios:

- `user_subnet -> restricted_subnet = deny`
- `admin_subnet -> restricted_subnet = allow`

Validated hybrid outcomes:

- aligned intended/offline/live happy path
- deterministic offline-side mismatch
- deterministic live-side mismatch

## Architecture Overview

```text
network-security-automation-framework/
|-- docs/
|-- labs/
|   |-- current_lab.yaml
|   `-- snapshots/
|-- src/
|   |-- framework/
|   |   |-- config/
|   |   |-- models/
|   |   `-- reporting/
|   |-- integration/
|   |-- live/
|   |-- offline/
|   `-- validators/
|-- tests/
|   |-- integration_tests/
|   |-- live_tests/
|   `-- offline_tests/
|-- conftest.py
|-- pytest.ini
`-- README.md
```

### Layering Model

- `*_service.py`
  Orchestrates request building, backend execution, and validator calls.
- `*_service_api.py`
  Owns backend-facing execution details only.
- `*_service_request.py`
  Builds request payloads and filter criteria.
- validators
  Assert meaning on normalized evidence instead of raw runtime output.
- tests
  Own suite metadata, Allure attachments, and scenario assertions.

This keeps the current architecture small, readable, and consistent across live, offline, and hybrid slices.

## Dual-Path Validation Model

### Live Path

Purpose:

- verify management-plane hardening expectations
- produce deterministic evidence without requiring real network hardware

Current state:

- backend is mocked
- running config is loaded from config defaults or explicit overrides
- hardening checks validate SSH presence, Telnet absence, and login banner presence

### Offline Path

Purpose:

- validate intended segmentation behavior before live deployment
- prove policy intent from a repository-safe snapshot

Current state:

- backend uses real PyBatfish
- snapshot is stored in `labs/snapshots/zero_trust_lab/`
- the two implemented scenarios use Batfish `testFilters`

### Hybrid Compliance Model

The hybrid slice correlates:

- intended access rule from the shared lab asset
- offline segmentation result from the Batfish-backed path
- live management-plane posture from the mocked live path

Those inputs are normalized into `HybridComplianceStatus`, which supports:

- pass/fail compliance outcomes
- explicit mismatch typing
- concise Allure reporting
- small suite-level aggregation summaries

## What Is Real Vs Mocked

Real in this repository:

- Batfish-backed offline segmentation validation
- Batfish snapshot assets checked into `labs/snapshots/`
- GitHub Actions execution shape for automated regression and reporting

Mocked by design:

- live device connectivity
- Scrapli/Nornir execution
- broader infrastructure orchestration
- large topology expansion

This is deliberate. The repo demonstrates backend-oriented QA automation design without pretending to automate production infrastructure end to end.

## Shared Lab Asset

The current lab asset in [labs/current_lab.yaml](labs/current_lab.yaml) drives:

- segment names and CIDRs
- intended management-plane posture
- intended access rule for hybrid validation
- offline segmentation expectations
- Batfish scenario metadata for the real offline path

That shared model keeps identifiers consistent across live, offline, and hybrid reporting.

## Tech Stack

- Python 3
- `pytest`
- `allure-pytest`
- `pydantic`
- `pyyaml`
- `pybatfish`
- Docker for the local Batfish runtime

## Setup

Install dependencies:

```bash
python -m pip install -r requirements.txt
```

Example environment defaults are provided in [.env.example](.env.example).

## Running Tests

Run the full repository:

```bash
python -m pytest -q
```

Run only the offline slice:

```bash
python -m pytest tests/offline_tests -q
```

Run only the integration slice:

```bash
python -m pytest tests/integration_tests -q
```

Important runtime note:

- the offline path starts and reuses a local `batfish/allinone` Docker container during test execution
- the live path remains mocked and does not require device access

## Allure Reporting

Generate results:

```bash
python -m pytest -q --alluredir=allure-results
```

Open a local report:

```bash
allure serve allure-results
```

Generate static output:

```bash
allure generate allure-results --clean -o allure-report
```

Current report shape stays compact:

- shared lab context
- live validation evidence
- offline reachability and Batfish summaries
- hybrid compliance evidence
- suite-level hybrid aggregation summaries

## CI/CD Overview

Included workflows:

- `PR Validation`
  Runs the lean pytest suite for pull requests and pushes to `main`.
- `Manual Run`
  Lets you trigger the repository test suite manually with custom pytest targets and arguments.
- `Run Suite`
  Reusable workflow that installs dependencies, pulls Batfish, runs pytest, and uploads Allure results.

Pipeline behavior:

- installs Python dependencies from `requirements.txt`
- pre-pulls `batfish/allinone` so offline validation can start quickly
- runs the same pytest suite used locally
- uploads Allure results as build artifacts

## This repository Demonstrates

- backend-oriented automation design instead of UI-heavy coverage
- documentation-first engineering discipline
- deterministic testing strategy with explicit scope control
- real offline policy validation through Batfish
- normalized compliance modeling for cross-path comparisons
- concise reporting suitable for scaled CI execution
- honest separation between mocked and real infrastructure

## Supporting Docs

- [implementation plan](docs/implementation-plan.md)
- [target architecture](docs/target-architecture.md)
- [live vs offline validation](docs/live-vs-offline-validation.md)
- [reporting and CI](docs/reporting-and-ci.md)
- [coding standards](docs/coding-standards.md)
