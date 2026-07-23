# EvoGuard Agent Change Admission Pilot

This public repository is a controlled consumer pilot for the pre-release
Agent Change Admission candidate captured from
[`EvoRiseKsa/EvoOM-Guard-m#147`](https://github.com/EvoRiseKsa/EvoOM-Guard-m/pull/147).
The feature was later published in `v4.3.0`, but this evidence remains bound to
the earlier candidate commit and candidate artifact identified below. It is not
evidence for the released `v4.3.0` bytes, the core product, a production
deployment, an independent audit, or a required merge gate.

The pilot tests one narrow decision: whether an exact PR change to
`calc/ops.py` matches a separately signed authorization, independently
re-derived raw Git facts, an isolated Guard verdict, and a distinct Trusted
Finalizer `ALLOW`.

## Evidence boundary

- The selected core commit is
  `31a9258277d2650aba24a1f9f009c25db1c4bbf0`.
- The externally retained experimental zipapp SHA-256 is
  `fcb9724de5e588e1664da5a108d077388bfaba1860d794d14142a2275f349842`.
- Three independent builds produced identical bytes. The artifact reports
  `evo-guard 4.2.0` because it was captured before the source version was
  bumped for publication. These candidate bytes were never a `v4.3.0` release
  asset and must not be described as one.
- The binary is a pilot-repository release asset, not a file in the candidate
  Git tree. Its hard-coded digest is the executable trust root; a missing or
  replaced asset fails closed.
- `EvoRiseKsa` and `MANA-awam` are controlled by the same owner. Their
  separation exercises GitHub permissions and artifact flow, but is not
  independent validation.

## Live workflow

The manual `EvoGuard Agent Change Pilot` workflow is installed only on the
default branch. It uses four boundaries:

1. protected metadata selects one exact open PR and creates an attempt-bound
   pending Check Run;
2. an unprivileged job executes the exact candidate with no secret or write
   permission and uploads claims only;
3. the `evoguard-agent-authorization` Environment exposes a distinct
   authorization key only after raw Git is re-derived and the fixed
   `calc/ops.py` scope is checked; and
4. the `evoguard-agent-finalizer` Environment exposes a different finalizer
   key, re-fetches Git objects, derives both binding families again, verifies
   Guard evidence, seals the admission, verifies it offline, and publishes
   retained evidence.

The protected Git executable is `/usr/bin/git`; its SHA-256 is stored as the
repository variable `EVOGUARD_GIT_EXECUTABLE_SHA256`. The no-secret
`EvoGuard Git Pin Probe` workflow is used to observe the current
`ubuntu-24.04` executable before enabling a pilot run. A runner-image change
fails closed until the pin is reviewed and updated.

## Scope and limits

The authorization permits exactly one modified file, `calc/ops.py`, no
deletions, at most one touched path, and at most 65,536 serialized candidate
bytes. Tests, workflows, configuration, signing keys, verifier packs, and
artifact-origin records are not in scope.

Docker with no network is defense in depth for this controlled sample. This
pilot does not establish that GitHub-hosted Docker is a sufficient isolation
boundary for arbitrary hostile code. It also does not prove patch correctness
beyond the declared verifier pack.

## Status

The bounded same-owner pilot is complete:

- one permitted change was accepted after both protected Environment
  approvals and independent offline verification of the retained `.evb`;
- one change that also added an ignored `dist/hidden.txt` path was rejected
  before authorization and produced no signed authorization or final bundle;
  and
- the exact permitted base/head pair was run again successfully. Its raw Git
  binding bytes were identical, while the authorization and final bundle were
  bound to the new workflow run.

See [`PILOT_RESULTS.md`](PILOT_RESULTS.md) for the immutable commits, run URLs,
digests, locally repeated checks, and limits of these results.

These results establish a working bounded protocol in this same-owner sample.
They do not establish an independent audit, general hostile-code isolation,
single-use authorization, production readiness, or a required merge gate.

`v4.3.0` was subsequently published from core commit
`b8c61315a22741415c75e4e8828feb60c0ad5149`. That release has a different
zipapp SHA-256,
`cb4b98cd1835cf3be5f92d25ad406fe504b43cc210a92201fd4eae8c6e61a70f`.
Publication does not retroactively convert this pilot's candidate artifact or
workflow runs into validation of the released artifact.

## License

This repository is source-available, not open source. See [`LICENSE`](LICENSE).
