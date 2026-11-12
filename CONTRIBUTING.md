# Contributing and team collaboration

Use a personal branch and pull request. Include the problem, change and verification.
Run `python -m pytest` and `ruff check .` before requesting review.
Do not change unknown outcomes into `None` without a valid non-elementarity decision.
Integration tests should compare derivatives, not just printer formatting.

## Small, independent team tasks

1. Build a sourced example set: at least 20 inputs, expected outcome and known primitives.
2. Install from a clean machine, follow the README and report reproducible failures;
   add regression tests or improve the guide.
3. Review the bilingual docs, run the demo against a one-minute timer, and improve the Q&A.
4. Review and understand the core design, integrate contributions and present the project.

Each member should submit their own real changes regularly through their GitHub account.
Tests, documentation fixes and reviewed examples are useful contributions. A generated
repository cannot supply a real team history or future recurring participation. Do not
backdate commits, impersonate members or invent collaboration records.

## AI disclosure

AI assistance is permitted in the stated assignment. This initial implementation used
OpenAI Codex for code, tests and documentation. Review generated work, disclose relevant
assistance, and be able to explain your own contributions in the course Q&A.

## Definition of done

- Public repository with real member contributions over time.
- Tests and clean-install smoke check pass.
- Versioned wheel/sdist uploaded to PyPI; homepage points to the Git repository.
- Motivation, contribution, examples, installation and limitations documented.
- Presenter rehearses a live demonstration under 60 seconds.
