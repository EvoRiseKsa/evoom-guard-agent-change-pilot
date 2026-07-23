from __future__ import annotations

import hashlib
import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BASE = "1" * 40
HEAD = "2" * 40
BASE_TREE = "3" * 40
HEAD_TREE = "4" * 40


def write(path: Path, value: object) -> None:
    path.write_text(
        json.dumps(value, sort_keys=True, separators=(",", ":")) + "\n",
        encoding="utf-8",
        newline="\n",
    )


def bindings(*, touched_paths: list[str] | None = None) -> dict[str, object]:
    touched = touched_paths or ["calc/ops.py"]
    return {
        "format": "EVOGUARD_AGENT_CHANGE_GIT_BINDINGS_V1",
        "base_sha": BASE,
        "head_sha": HEAD,
        "base_tree_sha": BASE_TREE,
        "head_tree_sha": HEAD_TREE,
        "candidate_sha256": "5" * 64,
        "candidate_size": 1024,
        "changed_paths": touched,
        "deleted_paths": [],
        "touched_paths": touched,
        "policy_sha256": "6" * 64,
        "verifier_pack_sha256": "7" * 64,
    }


def test_proposal_is_canonical_and_binds_verdict_bytes(tmp_path: Path) -> None:
    bindings_path = tmp_path / "bindings.json"
    verdict_path = tmp_path / "verdict.json"
    output = tmp_path / "proposal.json"
    write(bindings_path, bindings())
    verdict_path.write_bytes(b'{"result":"PASS"}\n')

    subprocess.run(
        [
            sys.executable,
            str(ROOT / "tools" / "create_proposal.py"),
            "--bindings",
            str(bindings_path),
            "--verdict",
            str(verdict_path),
            "--repository",
            "EvoRiseKsa/evoom-guard-agent-change-pilot",
            "--pr-number",
            "1",
            "--base-sha",
            BASE,
            "--head-sha",
            HEAD,
            "--guard-outcome",
            "PASS",
            "--out",
            str(output),
        ],
        check=True,
    )

    raw = output.read_bytes()
    proposal = json.loads(raw)
    assert raw == (
        json.dumps(proposal, ensure_ascii=False, sort_keys=True, separators=(",", ":")) + "\n"
    ).encode()
    assert proposal["intent"]["declared_paths"] == ["calc/ops.py"]
    assert proposal["claims"] == [
        {
            "id": "guard-verdict",
            "outcome": "PASS",
            "evidence_sha256": hashlib.sha256(verdict_path.read_bytes()).hexdigest(),
        }
    ]


def test_authorization_inputs_are_fixed_to_one_non_deleted_path(tmp_path: Path) -> None:
    bindings_path = tmp_path / "bindings.json"
    write(bindings_path, bindings())
    source = tmp_path / "source.json"
    scope = tmp_path / "scope.json"
    required = tmp_path / "required.json"

    subprocess.run(
        [
            sys.executable,
            str(ROOT / "tools" / "create_authorization_inputs.py"),
            "--bindings",
            str(bindings_path),
            "--repository",
            "EvoRiseKsa/evoom-guard-agent-change-pilot",
            "--repository-id",
            "123",
            "--pr-number",
            "1",
            "--run-id",
            "456",
            "--run-attempt",
            "1",
            "--base-sha",
            BASE,
            "--head-sha",
            HEAD,
            "--base-tree-sha",
            BASE_TREE,
            "--head-tree-sha",
            HEAD_TREE,
            "--source-out",
            str(source),
            "--scope-out",
            str(scope),
            "--required-out",
            str(required),
        ],
        check=True,
    )

    assert json.loads(scope.read_text(encoding="utf-8")) == {
        "allowed_patterns": ["calc/ops.py"],
        "maximum_touched_paths": 1,
        "maximum_candidate_bytes": 65536,
        "allow_deletions": False,
    }
    assert json.loads(required.read_text(encoding="utf-8")) == {
        "policy_sha256": "6" * 64,
        "verifier_pack_sha256": "7" * 64,
    }


def test_authorization_inputs_reject_an_extra_path(tmp_path: Path) -> None:
    bindings_path = tmp_path / "bindings.json"
    write(bindings_path, bindings(touched_paths=["calc/ops.py", "dist/hidden.txt"]))
    result = subprocess.run(
        [
            sys.executable,
            str(ROOT / "tools" / "create_authorization_inputs.py"),
            "--bindings",
            str(bindings_path),
            "--repository",
            "EvoRiseKsa/evoom-guard-agent-change-pilot",
            "--repository-id",
            "123",
            "--pr-number",
            "1",
            "--run-id",
            "456",
            "--run-attempt",
            "1",
            "--base-sha",
            BASE,
            "--head-sha",
            HEAD,
            "--base-tree-sha",
            BASE_TREE,
            "--head-tree-sha",
            HEAD_TREE,
            "--source-out",
            str(tmp_path / "source.json"),
            "--scope-out",
            str(tmp_path / "scope.json"),
            "--required-out",
            str(tmp_path / "required.json"),
        ],
        check=False,
        capture_output=True,
        text=True,
    )

    assert result.returncode != 0
    assert "limited to exactly calc/ops.py" in result.stderr
