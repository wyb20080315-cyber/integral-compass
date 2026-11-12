# Changelog

## 0.2.0

- Second argument is depth=None; root is level 1 and parts decisions advance a level.
- Search both factor orientations; None means exhausted bounded search, unknown is a string.
- IntegralSolver class prints successful DI/partial-fraction steps and displays the search tree.
- Unlimited-depth iterative deepening, deadline handling and cycle detection.
- Preserve the 0.1 Risch contract in integral_compass.classic and --classic.
- Minimal cases and Windows setup/offline test-kit instructions.
- Breaking API change: the new variable argument is keyword-only.

## 0.1.0

- Polynomial and finite DI integration with structured table rows.
- Rational-function polynomial division, partial fractions and term explanations.
- SymPy Risch adapter: `None` only for certified non-elementary remainders.
- Explicit unknown results, derivative verification and a subprocess deadline.
- Restricted expression parser, Python API, JSON/text CLI, bilingual documentation.
- Automated tests, build checks, a release workflow and classroom demo materials.
