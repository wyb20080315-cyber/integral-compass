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
