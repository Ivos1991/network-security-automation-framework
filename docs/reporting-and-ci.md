# Reporting And CI

## Reporting

Allure is the reporting solution for this repository.

## Reporting Principles

- Allure annotations belong in tests
- shared attachment helpers belong in `src/framework/reporting/`
- services should return structured results, not format Allure output
- technical evidence should be attached consistently across live and offline flows

## Planned Evidence Types

### Live Validation Evidence

- command metadata
- sanitized command output excerpts
- parsed management-plane facts
- device identity and role context

### Offline Validation Evidence

- snapshot name and source path
- Batfish question summary
- answer table summary
- intended topology or policy snippets relevant to the assertion

### Integration Evidence

- intended vs observed comparison table
- compliance/drift summary
- correlation keys such as hostnames, interfaces, zones, and routes

## Attachment Strategy

Collect compact but meaningful evidence:

- always attach a structured validation summary
- attach technical details on failure by default
- keep pass-path attachments lightweight
- sanitize secrets, IPs, or credentials where necessary for portfolio safety

## CI Direction

The first CI phase should stay small and credible.

## Initial Workflow Shape

- PR validation for offline tests and small suite tests
- manual workflow for selectable live, offline, or hybrid runs
- optional scheduled run for broader lab checks later

## Execution Guidance

- offline validations should be the default CI safety net
- live validations should run manually or in controlled scheduled contexts
- Allure results should be published as artifacts in every workflow
- environment configuration should remain externalized and minimal

## Current Workflow Shape

The repository now uses a small GitHub Actions setup that matches the current scope:

- `Run Suite`
  - reusable workflow for installing dependencies, pulling Batfish, running pytest, and uploading Allure artifacts
- `PR Validation`
  - runs the lean repository suite on pull requests and pushes to `main`
- `Manual Run`
  - supports manual execution with a selectable pytest target and extra arguments

## Current CI Boundaries

- CI exercises the real Batfish-backed offline path
- CI keeps the live path mocked
- CI does not attempt broader infrastructure orchestration
- Allure results are uploaded for every run

## Portfolio-Safe Positioning

This repository should demonstrate senior-level test architecture without pretending to automate production networks. The CI story should highlight reproducible lab execution, clear evidence, and conservative handling of live connectivity.
