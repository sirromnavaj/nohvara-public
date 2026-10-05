"""Partial pooling of success rates (empirical-Bayes Beta-Binomial), within a branch of a hierarchy.

The problem: a unit with 3 observations and a 67% success rate tells you very little. Its own rate is noise, while
the overall rate ignores what makes it different. Partial pooling sits between the two: each unit's estimate is
pulled toward its group's mean, and the pull is strongest where the unit's evidence is thinnest.

The trap: pool only units that belong together. Mixing a large population with a different base rate into the
pool (e.g. thousands of auto-generated jobs that are mostly cancelled) drags every small unit toward the wrong mean.
That's why `pool_by_branch` exists: pooling happens inside each branch, never across them.

    pooled_rate = (successes + kappa * p0) / (n + kappa)

p0 is the branch's pooled mean. kappa (prior strength) is estimated from how much the units actually differ
(method of moments), clipped to a sane range.
"""
from __future__ import annotations

from typing import Callable, Dict, Tuple

Units = Dict[str, Tuple[int, int]]          # key -> (successes, trials)


def pool(units: Units, kappa_min: float = 2.0, kappa_max: float = 200.0) -> tuple[float, float, dict]:
    """Return (p0, kappa, {key: pooled_rate}) for one branch."""
    tot_s = sum(s for s, n in units.values())
    tot_n = sum(n for s, n in units.values())
    if tot_n == 0:
        return 0.0, 0.0, {}
    p0 = tot_s / tot_n
    rates = [(s / n, n) for s, n in units.values() if n > 0]
    if len(rates) >= 2 and 0 < p0 < 1:
        w = sum(n for _, n in rates)
        between = sum(n * (r - p0) ** 2 for r, n in rates) / w     # weighted spread between units
        noise = p0 * (1 - p0) / (w / len(rates))                   # spread expected from sampling alone
        excess = between - noise
        kappa = (p0 * (1 - p0) / excess - 1) if excess > 0 else kappa_max
    else:
        kappa = 20.0
    kappa = max(kappa_min, min(kappa_max, kappa))
    return p0, kappa, {k: (s + kappa * p0) / (n + kappa) for k, (s, n) in units.items()}


def pool_by_branch(units: Units, branch_of: Callable[[str], str]) -> dict:
    """Pool separately inside each branch: {branch: (p0, kappa, {key: pooled})}."""
    branches: dict = {}
    for k, v in units.items():
        branches.setdefault(branch_of(k), {})[k] = v
    return {b: pool(u) for b, u in branches.items()}
