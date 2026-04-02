# Coding Standards

## General

- prefer explicit behavior over hidden automation
- keep modules small and responsibility-focused
- design for deterministic local execution first
- keep portfolio samples safe, minimal, and reproducible
- use type hints and Pydantic models where they clarify contracts

## Naming

- keep service modules named `<domain>_service.py`, `<domain>_service_api.py`, and `<domain>_service_request.py`
- use validation names that reflect security intent
- name result models by what they represent, not by the tool that produced them

## Layer Boundaries

- tests call service-layer functions, not Nornir, Scrapli, or Batfish directly
- service modules orchestrate flow and return structured results
- `*_service_api.py` stays runtime-facing and thin
- `*_service_request.py` shapes requests and filters only
- execution adapters own retries, connection handling, and normalization entry points
- validators consume normalized evidence rather than raw command output where practical

## Config

- expose settings through a root `config` fixture
- keep environment variables and YAML inputs small and explicit
- keep credentials external to checked-in files
- centralize runtime toggles for live, offline, and hybrid execution

## Fixtures

- keep root fixtures infrastructure-oriented
- keep scenario fixtures local
- the fixture that creates mutable state owns cleanup
- prefer read-only validations in the early slices

## Reporting

- Allure suites and scenario annotations belong in tests
- reusable attachment helpers belong in `src/framework/reporting/`
- attach focused technical evidence, not noisy dumps
- sanitize secrets before attachment

## Assertions

- assert security meaning, not parser trivia
- keep comparisons on normalized structures
- prefer clear failure messages that explain what policy was violated
- separate evidence gathering from assertion logic

## Logging

- use structured logging for execution details
- avoid printing raw secrets, credentials, or full sensitive configs
- keep debug-level command traces optional and configuration-driven
