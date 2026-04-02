from __future__ import annotations

from typing import Any

from assertpy import assert_that


def expect_that(actual: Any, description: str):
    """Return an assertpy builder with a mandatory human-readable description."""
    return assert_that(actual, description=description)
