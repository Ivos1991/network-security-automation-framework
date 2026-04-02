# Reusable Patterns

## Structural Patterns To Preserve

### 1. Layered Repository Shape

Use a framework-owned core plus domain-owned service modules:

- `src/framework/` for config, execution adapters, reporting, logging, and shared models
- `src/services/` for validation services and service contracts
- `tests/` for live, offline, integration, and suite coverage

### 2. Service / API / Request Split

Preserve the naming and separation style from the earlier repositories:

- `<domain>_service.py`
- `<domain>_service_api.py`
- `<domain>_service_request.py`

For this project:

- `*_service.py` orchestrates validation flow
- `*_service_api.py` invokes Nornir/Scrapli/Batfish adapters
- `*_service_request.py` shapes validated request objects for the execution layer

### 3. Explicit Runtime Profiles

Keep runtime selection configuration-driven rather than test-driven:

- `live`
- `offline`
- `hybrid`

Tests should select behavior through fixtures, markers, and config instead of embedding branching logic in assertions.

### 4. Root And Local Fixture Ownership

- root `conftest.py` owns config, runtime selectors, Allure hooks, and shared logging
- `tests/live_tests/**/conftest.py` owns lab target fixtures and connection-scoped setup
- `tests/offline_tests/**/conftest.py` owns intended topology/config fixtures
- `tests/integration_tests/**/conftest.py` owns cross-path scenario composition

### 5. Shared Validator Contract

A validator should consume normalized evidence and return a structured result regardless of source.

Example concerns:

- hardening validator
- segmentation validator
- routing validator
- drift/compliance validator

## Patterns To Preserve With Improvement

### Config Passing

Preserve the visible `config` fixture pattern, but keep it smaller and strongly typed through Pydantic settings and models.

### Allure Integration

Preserve Allure in tests and shared reporting helpers in the framework layer.

Improve by standardizing attachments for:

- command outputs
- parsed device facts
- Batfish answer summaries
- topology/policy snapshots

### Logging

Keep technical logging framework-owned. Service modules can emit domain events, but command-level traces and retries should stay in shared execution utilities.

### Portfolio Safety

Keep the repository demo-safe:

- use lab-safe inventory examples
- isolate secrets from checked-in samples
- avoid vendor-sensitive production details
- prefer small reproducible topologies over broad enterprise claims

## Patterns Not To Carry Forward

- oversized global fixture registries
- transport-specific logic leaking into tests
- scenario reporting embedded inside services
- tightly coupled environment-specific config sprawl
- one-off helper modules that bypass the layered architecture
