"""Judge-owned protocol tests for the pilot CLI; never import candidate code."""

from __future__ import annotations

import os
import subprocess
import sys


EXEC = os.environ["EVOGUARD_EXEC"]
PYTHON = os.environ.get("EVOGUARD_PYTHON", sys.executable)


def run_add(left: int, right: int) -> str:
    result = subprocess.run(
        [EXEC, PYTHON, "-m", "calc", "add", str(left), str(right)],
        capture_output=True,
        check=False,
        text=True,
        timeout=15,
    )
    assert result.returncode == 0, result.stderr
    return result.stdout.strip()


def test_adds_small_operands() -> None:
    assert run_add(2, 3) == "5"


def test_adds_larger_operands() -> None:
    assert run_add(10, 20) == "30"
