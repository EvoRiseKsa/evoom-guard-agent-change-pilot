# Agent Change Admission pilot results

Date: 2026-07-23

This record covers a public, same-owner consumer pilot of the unreleased
Agent Change Admission candidate from
[`EvoRiseKsa/EvoOM-Guard-m#147`](https://github.com/EvoRiseKsa/EvoOM-Guard-m/pull/147).
It reports observed results, not a release claim or an independent security
assessment.

## Fixed inputs

- Pilot protected base:
  `8dd5a4b03d886c289bbabf1fd9e37cbda99f6f8a`
- Candidate core commit:
  `31a9258277d2650aba24a1f9f009c25db1c4bbf0`
- Candidate zipapp SHA-256:
  `fcb9724de5e588e1664da5a108d077388bfaba1860d794d14142a2275f349842`
- Trusted-base policy SHA-256:
  `0dbc18dd892e8322d777d58ed564e90c8a1ec59b5986318dbf1aa8d12e8f41f8`
- Verifier-pack SHA-256:
  `e6823b20e38f375a9459e49c3fd4f68f0ca96697c654537e381b0320a93016d8`
- Permitted scope: exactly `calc/ops.py`, no deletions, one touched path,
  and at most 65,536 serialized candidate bytes.

The candidate artifact still reports `evo-guard 4.2.0`; it is an unreleased
PR artifact and is not a v4.3 release.

## Round 1: permitted change

- Pull request:
  [`MANA-awam` PR #1](https://github.com/EvoRiseKsa/evoom-guard-agent-change-pilot/pull/1)
- Base:
  `8dd5a4b03d886c289bbabf1fd9e37cbda99f6f8a`
- Head:
  `a44ce74419386cde16c4b7dfb9ee9915c4a2b39c`
- Diff: one addition and one deletion in `calc/ops.py`.
- Workflow:
  [run 29983466826](https://github.com/EvoRiseKsa/evoom-guard-agent-change-pilot/actions/runs/29983466826)
- Observed result: `metadata`, `reverify`, `authorize`, `finalize`, and
  `reconcile` all succeeded; the attempt-bound Check Run concluded `success`.

The retained manifest covered five final files and passed an independent
local SHA-256 check. The downloaded final bundle was then verified locally
with the candidate zipapp, the two public keys, the independently retained
source/context files, and the finalizer Git bindings. The verifier returned:

```text
decision ALLOW
ok true
touched_paths ["calc/ops.py"]
candidate_sha256 4a049063867045dca61214015f9ccae75a3a3eeadbc40d8a5987a80ca19c8763
```

The producer, authorizer, and finalizer raw Git binding files had identical
bytes with SHA-256:

```text
7311b6b780eb192daf9547997eaaa830b38d0314943e01cae0427fdb1aebd007
```

## Round 2: ignored-path bypass attempt

- Pull request:
  [`MANA-awam` PR #2](https://github.com/EvoRiseKsa/evoom-guard-agent-change-pilot/pull/2)
- Base:
  `8dd5a4b03d886c289bbabf1fd9e37cbda99f6f8a`
- Head:
  `5b490d3d7f662b8f3461259bcfa3ef30f6bd5a4b`
- Diff: `calc/ops.py` plus tracked `dist/hidden.txt`.
- Workflow:
  [run 29983731021](https://github.com/EvoRiseKsa/evoom-guard-agent-change-pilot/actions/runs/29983731021)
- Observed result: `reverify` succeeded, but the raw Git authorization inputs
  contained both paths. `authorize` failed with
  `pilot authorization is limited to exactly calc/ops.py`; `finalize` was
  skipped and the Check Run concluded `failure`.

Only the untrusted and control artifacts were retained. GitHub reported no
authorization artifact and no finalized `.evb`. This is the expected
fail-closed result: an ignored path in the candidate-copy optimization did
not disappear from the authoritative raw Git binding.

## Exact-change replay

The exact Round 1 PR, base, and head were dispatched again in
[run 29983835620](https://github.com/EvoRiseKsa/evoom-guard-agent-change-pilot/actions/runs/29983835620).
All five stages succeeded and the downloaded replay bundle independently
verified as `ALLOW`.

The replay raw Git binding file was byte-for-byte identical to Round 1 and
retained SHA-256
`7311b6b780eb192daf9547997eaaa830b38d0314943e01cae0427fdb1aebd007`.
The authorization and final bundle bytes differed because their context was
bound to workflow run `29983835620` instead of `29983466826`. This proves
deterministic binding of the same exact Git change and fresh run identity. It
also establishes that the V1 protocol is idempotent for an unchanged
base/head pair; it is not a single-use or replay-prevention protocol.

## What these observations establish

Within this bounded public sample, the workflow:

1. kept the unprivileged Guard execution separate from both signing keys;
2. independently re-derived raw Git facts before authorization and again
   before finalization;
3. bound the final decision to repository identity, exact Git objects,
   candidate bytes, policy, verifier pack, Guard artifact, and workflow run;
4. rejected a tracked path that the candidate-copy optimization ignored; and
5. produced a retained bundle that could be verified offline.

## What these observations do not establish

- `EvoRiseKsa` and `MANA-awam` have the same owner. The experiment exercises
  separate GitHub identities, protected Environments, approvals, secrets,
  artifacts, and jobs, but is not independent organizational validation.
- Human Environment approval is an operational control in this pilot, not
  proof that the approver inspected every derived byte.
- The experiment does not prove that GitHub-hosted Docker is sufficient
  isolation for arbitrary hostile code.
- The verifier pack proves only its declared sample properties.
- The workflow is manual and is not a production or required merge gate.
- The candidate has not been released as v4.3.
- The protocol does not provide authorization revocation or single-use replay
  prevention.
