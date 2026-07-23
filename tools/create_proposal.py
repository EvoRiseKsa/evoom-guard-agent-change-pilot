"""Create the bounded untrusted proposal used by the controlled pilot."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
from pathlib import Path

GIT_SHA = re.compile(r"(?:[0-9a-f]{40}|[0-9a-f]{64})\Z")
SHA256 = re.compile(r"[0-9a-f]{64}\Z")


def read_object(path: Path) -> dict[str, object]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise SystemExit(f"{path} must contain one JSON object")
    return value


def canonical_write(path: Path, value: object) -> None:
    path.write_text(
        json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":")) + "\n",
        encoding="utf-8",
        newline="\n",
    )


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--bindings", type=Path, required=True)
    parser.add_argument("--verdict", type=Path, required=True)
    parser.add_argument("--repository", required=True)
    parser.add_argument("--pr-number", type=int, required=True)
    parser.add_argument("--base-sha", required=True)
    parser.add_argument("--head-sha", required=True)
    parser.add_argument("--guard-outcome", choices=("PASS", "FAIL"), required=True)
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()

    if args.pr_number < 1:
        raise SystemExit("PR number must be positive")
    if not GIT_SHA.fullmatch(args.base_sha) or not GIT_SHA.fullmatch(args.head_sha):
        raise SystemExit("base/head SHA is invalid")
    if args.out.exists():
        raise SystemExit("refusing to replace an existing proposal")

    bindings = read_object(args.bindings)
    required = {
        "format",
        "base_sha",
        "head_sha",
        "base_tree_sha",
        "head_tree_sha",
        "candidate_sha256",
        "candidate_size",
        "changed_paths",
        "deleted_paths",
        "touched_paths",
        "policy_sha256",
        "verifier_pack_sha256",
    }
    if set(bindings) != required:
        raise SystemExit("bindings have a non-canonical key set")
    if bindings["format"] != "EVOGUARD_AGENT_CHANGE_GIT_BINDINGS_V1":
        raise SystemExit("bindings format is unsupported")
    if bindings["base_sha"] != args.base_sha or bindings["head_sha"] != args.head_sha:
        raise SystemExit("bindings do not match the selected PR revisions")
    for key in ("candidate_sha256", "policy_sha256"):
        if not isinstance(bindings[key], str) or not SHA256.fullmatch(bindings[key]):
            raise SystemExit(f"bindings {key} is invalid")
    pack = bindings["verifier_pack_sha256"]
    if pack is not None and (not isinstance(pack, str) or not SHA256.fullmatch(pack)):
        raise SystemExit("bindings verifier_pack_sha256 is invalid")
    for key in ("changed_paths", "deleted_paths", "touched_paths"):
        value = bindings[key]
        if (
            not isinstance(value, list)
            or any(not isinstance(item, str) or not item for item in value)
            or value != sorted(set(value))
        ):
            raise SystemExit(f"bindings {key} is not a sorted unique path list")
    if bindings["touched_paths"] != sorted(
        set(bindings["changed_paths"]) | set(bindings["deleted_paths"])
    ):
        raise SystemExit("bindings touched paths are not the changed/deleted union")

    verdict_bytes = args.verdict.read_bytes()
    if not verdict_bytes or len(verdict_bytes) > 64 * 1024 * 1024:
        raise SystemExit("verdict is empty or outside the pilot limit")
    evidence_sha256 = hashlib.sha256(verdict_bytes).hexdigest()
    proposal = {
        "format": "EVOGUARD_AGENT_CHANGE_PROPOSAL_V1",
        "producer": {
            "id": "mana-pilot-repair-agent",
            "kind": "automated-repair",
            "version": "round-1",
        },
        "source": {
            "repository": args.repository,
            "pull_request_number": args.pr_number,
            "base_sha": args.base_sha,
            "head_sha": args.head_sha,
        },
        "intent": {
            "summary": "Controlled same-owner repair of the calculator implementation.",
            "declared_paths": bindings["touched_paths"],
        },
        "change": {
            "candidate_sha256": bindings["candidate_sha256"],
            "candidate_size": bindings["candidate_size"],
            "changed_paths": bindings["changed_paths"],
            "deleted_paths": bindings["deleted_paths"],
            "touched_paths": bindings["touched_paths"],
        },
        "observed_policy": {
            "policy_sha256": bindings["policy_sha256"],
            "verifier_pack_sha256": pack,
        },
        "claims": [
            {
                "id": "guard-verdict",
                "outcome": args.guard_outcome,
                "evidence_sha256": evidence_sha256,
            }
        ],
    }
    canonical_write(args.out, proposal)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
