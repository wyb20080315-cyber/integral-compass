# Changelog

## 0.4.0

- Return the exact string "None, verified by Risch" for automatic non-elementarity proofs.
- Include cause and explanation in every new-API unknown return message.
- Add structured reason_code and value to reports/JSON, preserving Python None for depth exhaustion.
- Distinguish unsupported root rules from unresolved integration-by-parts directions.
- Add a concise one-minute presentation script, real minimal failure cases, and explicitly simulated internal faults.
- Keep the classic compatibility API unchanged.

## 0.3.0

- Detect return to the original integrand, including constant multiples, before the depth boundary.
- Carry full integration-by-parts coefficients to solve cyclic equations; reject J=J identities.
- When depth is None, automatically combine Risch decisions with classroom search.
- Share the total time budget (default 10 seconds): 30% for Risch, the remainder for search.
- Preserve finite-depth None/exhausted, add automatic None/non_elementary, keep unknown distinct.
- Add cyclic/default-mode cases and refresh the Windows offline kit.

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
