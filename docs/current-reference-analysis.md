# Current Reference Analysis

## Planning Objective

This repository should follow a documentation-first workflow while adapting the structure to network security validation.

The framework should reuse only the patterns that fit this problem space:

- root planning docs before code
- explicit `config` fixture ownership
- modular `service -> service_api -> service_request` layering
- Allure-centered reporting
- local reproducibility first
- portfolio-safe separation between framework code and target-specific data

## Stable Patterns Worth Preserving

### Documentation Flow

Architecture, fixtures, reporting, and coding standards should be established before implementation. That sequence should remain unchanged here.

### Service Layer Shape

The service-oriented repository uses a clean split:

- `*_service.py` for test-facing orchestration
- `*_service_api.py` for execution-layer calls
- `*_service_request.py` for shaped request inputs

That pattern is still useful even though this project is not HTTP-centric. Here, "API" means the execution adapter for a runtime such as Nornir or Batfish.

### Fixture Boundaries

The project should avoid hiding scenario-specific state in the root `conftest.py`:

- root `conftest.py` owns config, runtime selection, logging, reporting hooks, and broad session setup
- local `conftest.py` files own topology fixtures, intended policy data, and scenario-specific setup

### Reporting Boundaries

Allure annotations belong in tests. Shared attachment helpers belong in the framework layer. Service modules should not interpret scenario meaning.

## Network-Specific Differences

This repository introduces network-specific concerns such as:

- device inventory and credentials
- command execution over SSH/API
- intended topology and policy models
- offline analysis of configurations and reachability
- lab reproducibility and safe handling of live targets

Because of that, the execution layer must support two modes that share validators but differ in evidence source:

1. live validation from device state
2. offline validation from intended configs and topology snapshots

## Architectural Direction Confirmed

The target design should preserve the familiar repository style while shifting the execution core from generic transport calls to network automation backends:

- framework config and reporting stay centralized
- execution adapters stay backend-specific and thin
- validators stay domain-focused and reusable
- tests call service-layer functions rather than backend libraries directly

## Constraints To Preserve

- repository must remain fully local with no remote configured yet
- docs-first planning must complete before code
- Allure remains the reporting solution
- architecture must stay modular and portfolio-safe
- implementation should begin with a narrow lab slice rather than a broad platform
