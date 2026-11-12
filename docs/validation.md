# Local validation record

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

The repository contains a Python/OS CI matrix, but this record does not claim those
remote jobs have run. PyPI publication requires account setup and is not established
by a successful local build. Recheck the workflow and index before claiming publication.
