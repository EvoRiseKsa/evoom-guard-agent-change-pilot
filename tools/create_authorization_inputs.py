"""Create fixed-scope control inputs from protected metadata and raw Git facts."""

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path

GIT_SHA = re.compile(r"(?:[0-9a-f]{40}|[0-9a-f]{64})\Z")
REPOSITORY = re.compile(r"[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+\Z")


def write(path: Path, value: object) -> None:
    if path.exists():
        raise SystemExit(f"refusing to replace {path}")
    path.write_text(
        json.dumps(value, sort_keys=True, separators=(",", ":")) + "\n",
        encoding="utf-8",
        newline="\n",
    )


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--bindings", type=Path, required=True)
    parser.add_argument("--repository", required=True)
    parser.add_argument("--repository-id", required=True)
    parser.add_argument("--pr-number", type=int, required=True)
    parser.add_argument("--run-id", required=True)
    parser.add_argument("--run-attempt", type=int, required=True)
    parser.add_argument("--base-sha", required=True)
    parser.add_argument("--head-sha", required=True)
    parser.add_argument("--base-tree-sha", required=True)
    parser.add_argument("--head-tree-sha", required=True)
    parser.add_argument("--source-out", type=Path, required=True)
    parser.add_argument("--scope-out", type=Path, required=True)
    parser.add_argument("--required-out", type=Path, required=True)
    args = parser.parse_args()

    if not REPOSITORY.fullmatch(args.repository):
        raise SystemExit("repository is invalid")
    if not args.repository_id.isdecimal() or int(args.repository_id) < 1:
        raise SystemExit("repository ID is invalid")
    if args.pr_number < 1 or args.run_attempt < 1:
        raise SystemExit("PR number and run attempt must be positive")
    if not args.run_id.isdecimal() or int(args.run_id) < 1:
        raise SystemExit("run ID is invalid")
    for value in (
        args.base_sha,
        args.head_sha,
        args.base_tree_sha,
        args.head_tree_sha,
    ):
        if not GIT_SHA.fullmatch(value):
            raise SystemExit("Git identity is invalid")

    bindings = json.loads(args.bindings.read_text(encoding="utf-8"))
    if not isinstance(bindings, dict):
        raise SystemExit("bindings must be one JSON object")
    exact = {
        "base_sha": args.base_sha,
        "head_sha": args.head_sha,
        "base_tree_sha": args.base_tree_sha,
        "head_tree_sha": args.head_tree_sha,
    }
    if any(bindings.get(key) != value for key, value in exact.items()):
        raise SystemExit("raw Git bindings do not match protected metadata")
    if bindings.get("touched_paths") != ["calc/ops.py"]:
        raise SystemExit("pilot authorization is limited to exactly calc/ops.py")
    if bindings.get("deleted_paths") != []:
        raise SystemExit("pilot authorization never permits a deletion")

    source = {
        "repository": args.repository,
        "repository_id": args.repository_id,
        "pull_request_number": args.pr_number,
        "authorization_run_id": args.run_id,
        "authorization_run_attempt": args.run_attempt,
        **exact,
    }
    scope = {
        "allowed_patterns": ["calc/ops.py"],
        "maximum_touched_paths": 1,
        "maximum_candidate_bytes": 65536,
        "allow_deletions": False,
    }
    required = {
        "policy_sha256": bindings.get("policy_sha256"),
        "verifier_pack_sha256": bindings.get("verifier_pack_sha256"),
    }
    write(args.source_out, source)
    write(args.scope_out, scope)
    write(args.required_out, required)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
