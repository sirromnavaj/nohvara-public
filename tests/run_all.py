"""Standard-library test runner: python tests/run_all.py (pytest also discovers the test_ functions)."""
import sqlite3
import sys
from pathlib import Path

R = Path(__file__).resolve().parents[1]
for sub in ("pooling", "ideas", "namespace", "packages/nohvara-paths/src"):
    sys.path.insert(0, str(R / sub))

from hierarchical_pool import pool, pool_by_branch  # noqa: E402
from idea_classifier import Idea, classify  # noqa: E402
from namespace import Namespace, NotFound  # noqa: E402


def test_pooling_shrinks_thin_evidence_most():
    p0, kappa, pooled = pool({"big": (900, 1000), "small": (2, 3), "mid": (40, 100)})
    assert abs(pooled["big"] - 0.9) < 0.02                       # strong evidence keeps its own rate
    assert abs(pooled["small"] - p0) < abs(2 / 3 - p0)           # thin evidence moves toward the mean
    assert min(0.4, p0) <= pooled["mid"] <= max(0.4, p0)


def test_branches_are_pooled_separately():
    units = {"env/a": (90, 100), "env/b": (2, 3), "sys/jobs": (240, 2800)}
    out = pool_by_branch(units, lambda k: k.split("/")[0])
    env_p0 = out["env"][0]
    assert env_p0 > 0.8                                          # the job population does not drag the env mean
    assert out["env"][2]["env/b"] > 0.7


def test_idea_lifecycle():
    i = Idea("weekly digest raises reply rate")
    try:
        i.record_test(True, "x")
        raise AssertionError("must refuse a test before a pre-registered metric")
    except ValueError:
        pass
    i.select("reply rate", ">= +10% vs baseline", 14)
    assert i.record_test(True, "week 1: +14%") == "inconclusive"   # one pass is not enough
    assert i.record_test(True, "week 2: +11%") == "validated"
    assert classify(1, 3) == "refuted"
    try:
        i.record_test(True, "")
        raise AssertionError("evidence is required")
    except ValueError:
        pass


def test_namespace_boundary_is_absence():
    ns = Namespace({"studio": {"state": "active", "tasks": ["t1"]}, "client": {"state": "ended", "tasks": ["old"]}},
                   {"lessons": ["l1"]})
    assert ns.ls("/root/env", env="studio") == ["studio"]
    try:
        ns.ls("/root/env/client", env="studio")
        raise AssertionError("another environment must be NOT FOUND")
    except NotFound:
        pass
    assert ns.ls("/root/env/client/tasks") == []                 # ended environment does no work
    assert ns.ls("/root/shared/lessons", env="studio") == ["l1"] # shared resources visible to every view


def test_choke_point_triggers():
    c = sqlite3.connect(":memory:")
    c.executescript((R / "patterns" / "choke_point_triggers.sql").read_text(encoding="utf-8"))
    c.execute("INSERT INTO tasks(id, title, status) VALUES (1, 't', 'pending')")
    c.execute("UPDATE tasks SET status='done' WHERE id=1")
    c.execute("UPDATE tasks SET status='done' WHERE id=1")      # no real change -> no event
    assert c.execute("SELECT COUNT(*) FROM task_events").fetchone()[0] == 1
    c.execute("INSERT INTO caps VALUES ('proposals', 2)")
    for t in ("a", "b", "c"):
        c.execute("INSERT INTO proposals(title) VALUES (?)", (t,))
    assert c.execute("SELECT COUNT(*) FROM proposals").fetchone()[0] == 2      # third ignored at cap
    assert c.execute("SELECT COUNT(*) FROM rejections").fetchone()[0] == 1     # ...and logged


def test_paths_root_declared(tmp=None):
    import os
    import tempfile
    import nohvara_paths as np
    with tempfile.TemporaryDirectory() as d:
        (Path(d) / np.MARKER).write_text("root marker")
        os.environ["NOHVARA_ROOT"] = d
        try:
            assert np.root() == Path(d)
        finally:
            del os.environ["NOHVARA_ROOT"]


if __name__ == "__main__":
    fails = 0
    for name, fn in sorted(globals().items()):
        if name.startswith("test_") and callable(fn):
            try:
                fn()
                print(f"PASS  {name}")
            except Exception as e:
                fails += 1
                print(f"FAIL  {name}: {type(e).__name__}: {e}")
    sys.exit(1 if fails else 0)
