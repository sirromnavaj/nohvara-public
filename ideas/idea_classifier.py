"""An idea warehouse: every idea is kept, and its status comes from testing it against reality.

Three rules this encodes:
  1. Untested isn't refuted. An idea nobody selected goes back to the warehouse; it isn't deleted.
  2. Declined isn't refuted either. A "no" from a reviewer is a decision, not evidence about the idea.
  3. No test without a pre-registered metric, threshold and window, and no verdict without evidence.

Belief in an idea is a Beta(alpha, beta) posterior updated by each test:
  validated     posterior mean >= 0.70 with at least 2 passes
  refuted       posterior mean <= 0.30 with at least 2 failures
  inconclusive  anything else - eligible for another test
"""
from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime

VALID_AT, REFUTED_AT, MIN_EVIDENCE = 0.70, 0.30, 2


def classify(alpha: float, beta: float) -> str:
    mean = alpha / (alpha + beta)
    if mean >= VALID_AT and (alpha - 1) >= MIN_EVIDENCE:
        return "validated"
    if mean <= REFUTED_AT and (beta - 1) >= MIN_EVIDENCE:
        return "refuted"
    return "inconclusive"


@dataclass
class Idea:
    title: str
    state: str = "warehoused"                # warehoused -> testing -> validated | refuted | inconclusive
    hypothesis: str = ""
    metric: str = ""
    threshold: str = ""
    window_days: int = 0
    alpha: float = 1.0
    beta: float = 1.0
    tests: list = field(default_factory=list)

    @property
    def belief(self) -> float:
        return self.alpha / (self.alpha + self.beta)

    def select(self, metric: str, threshold: str, window_days: int, hypothesis: str = "") -> None:
        if not (metric and threshold and window_days):
            raise ValueError("pre-register the test first: metric, threshold and window_days")
        self.metric, self.threshold, self.window_days, self.hypothesis = metric, threshold, window_days, hypothesis
        self.state = "testing"

    def record_test(self, passed: bool, evidence: str) -> str:
        if not evidence:
            raise ValueError("a verdict without evidence is not a test")
        if not self.metric:
            raise ValueError("select() the idea with a pre-registered test before recording results")
        self.alpha += 1 if passed else 0
        self.beta += 0 if passed else 1
        self.tests.append({"at": datetime.now().isoformat(timespec="seconds"), "passed": passed, "evidence": evidence})
        self.state = classify(self.alpha, self.beta)
        return self.state
