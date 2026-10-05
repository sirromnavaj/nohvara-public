"""nohvara_paths - where the Nohvara vault is, as ONE versioned package (packages step 1, 2026-10-05).

WHY. 765 modules carry their own copy of
    ROOT = next((p for p in Path(__file__).resolve().parents if (p / "CLAUDE.md").exists()), ...)
which only works when the code sits inside the vault tree. A package installed on another node (the fleet VPS, a
future owned host) is NOT inside a vault, so it needs the root DECLARED: NOHVARA_ROOT wins, then a walk up from the
caller, then from the working directory. Unknown is an error, never a silent guess.
"""
from __future__ import annotations

import os
from pathlib import Path

__version__ = "0.1.0"
MARKER = "CLAUDE.md"


class RootNotFound(RuntimeError):
    pass


def _walk(start: Path) -> Path | None:
    start = start.resolve()
    for p in (start, *start.parents):
        if (p / MARKER).exists():
            return p
    return None


def root(start: str | os.PathLike | None = None) -> Path:
    """The vault root: $NOHVARA_ROOT, else the first ancestor of `start` (or cwd) holding CLAUDE.md."""
    env = os.environ.get("NOHVARA_ROOT")
    if env:
        p = Path(env).expanduser()
        if not (p / MARKER).exists():
            raise RootNotFound(f"NOHVARA_ROOT={p} has no {MARKER}")
        return p
    for s in ([Path(start)] if start else []) + [Path.cwd()]:
        hit = _walk(s if s.is_dir() else s.parent)
        if hit:
            return hit
    raise RootNotFound("no Nohvara vault found: set NOHVARA_ROOT or run inside the vault")


def data_dir(start=None) -> Path:
    return root(start) / "data"


def db_path(start=None) -> Path:
    return data_dir(start) / "nohvara.db"


def spool_dir(start=None) -> Path:
    return data_dir(start) / "write_spool"
