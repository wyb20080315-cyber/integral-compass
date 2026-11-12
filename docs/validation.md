# Validation records

## 0.4 explanatory outcomes and presentation cases

Python 3.12 / SymPy 1.14.0: all 96 local tests passed, including the unchanged
classic contract. Ruff and the real failure-case/presentation scripts passed.
The diagnostics explicitly distinguish Python None from the Risch-certificate
string, root unsupported rules from unresolved directions, timeouts, injected
worker failures and forced verification failure. Simulated faults are labeled
and do not claim to be normal mathematical inputs.
The refreshed distributions/offline kit and cross-platform CI are checked separately.

## 0.3 cyclic equations and automatic Risch

The cycle/default-mode changes passed 89 local tests on Python 3.12 with SymPy 1.14.0.
After simplifying timeout-mode selection, the 39 search/auto tests were rerun and passed;
the original 50 classic tests remain unchanged. Seven minimal cases passed.
New coverage includes signed/scaled recurrences, depth-boundary closure, rejection of
degenerate identities, independent summand equations, Risch certificates versus unknown,
Risch fallback and preservation of automatic mode with an explicit timeout.
The refreshed 0.3 distributions and offline test kit are validated separately.

## 0.2 depth-controlled search

Locally validated on Python 3.12 with SymPy 1.14.0: 74 tests passed, Ruff passed,
and the five user-facing minimal cases passed. The wheel and source distribution
passed Twine checks. The Windows x64 Python installer was downloaded unchanged
from python.org; its URL and SHA256 are documented in windows.zh-CN.md.
An offline test kit bundles the package, SymPy and mpmath wheels.

The new tests exercise root-level counting, both directions and all four third-level
leaves, deeper success after bounded exhaustion, reverse-direction success,
actual partial-fraction leaves, unbounded search, cycles, unknown propagation,
timeouts, class output/caching, custom symbols, linearity and CLI behavior.
The 50 original tests continue to verify the separate classic contract.

The CI record below applies to 0.1. The 0.2 PR subsequently passed all five test jobs
and its build job in run 43161174564; its expanded suite had 74 tests.

## 0.1 local checks

Validated on Python 3.12 in the managed Linux workspace on 2026-11-12.

| Check | Observed result |
| --- | --- |
| Ruff | Passed |
| Tests with SymPy 1.14.0 | 50 passed |
| Tests with SymPy 1.13.3, isolated environment | 50 passed |
| Build wheel and source distribution | Passed |
| Twine metadata/README checks | Passed |
| Wheel installation outside the source tree, with fresh dependencies | Passed |
| CLI DI example from the clean installation | Verified elementary result |

Tests cover polynomial, DI and repeated-factor rational examples; independent numerical
derivative samples; nested logarithms; certified non-elementary remainders; unknown
outcomes; invalid/code-like inputs; timeouts; custom symbols; CLI output/exit codes;
and rejection of unverified or merely unevaluated backend results.

The Linux development environment's preinstalled AnyIO plugin emitted a pytest
deprecation warning. The isolated compatibility environment passed without that warning.

## GitHub Actions

[CI run 43154771884](https://github.com/wyb20080315-cyber/integral-compass/actions/runs/43154771884)
passed all six jobs for source commit `a0f794d171d8532383d9939e5e45efad2093372b`:

- Ubuntu: Python 3.10 with SymPy 1.13.3, and Python 3.11, 3.12, 3.13 with SymPy 1.14.0.
- Windows: Python 3.12 with SymPy 1.14.0.
- Build, distribution checks and installation of the wheel outside the source checkout.

Each of the five test jobs passed the 50-test suite. Subsequent documentation-only
updates record these results without changing the tested Python source.

PyPI publication requires account setup and is not established by a successful build
or CI run. Recheck the publishing workflow and index before claiming publication.
