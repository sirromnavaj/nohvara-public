"""A Plan 9-style namespace: one tree of named resources; each environment sees only its own part.

In Plan 9 every process has its own namespace: what isn't mounted there simply doesn't exist for it. The same idea
makes a clean isolation boundary between environments (projects, clients, ventures) running on one system:

  /root/env/<id>          an environment's own subtree (only visible to itself, or to the operator view)
  /root/shared/<name>     shared, read-only resources every view mounts (e.g. distilled lessons)

Asking for another environment's path raises NotFound - never "permission denied", which would leak that the
thing exists. An ENDED environment's work resolves to nothing.
"""
from __future__ import annotations


class NotFound(LookupError):
    pass


class Namespace:
    def __init__(self, environments: dict, shared: dict):
        """environments: id -> {"state": "active"|"ended", "tasks": [...]}; shared: name -> value."""
        self.envs, self.shared = environments, shared

    def view(self, env: str | None = None) -> dict:
        if env is None:
            return {"env": sorted(self.envs), "shared": sorted(self.shared)}
        if env not in self.envs:
            raise NotFound(f"/root/env/{env}")
        return {"env": [env], "shared": sorted(self.shared)}

    def ls(self, path: str, env: str | None = None):
        parts = [p for p in path.strip("/").split("/") if p]
        if not parts or parts[0] != "root":
            raise NotFound(path)
        v = self.view(env)
        if len(parts) == 1:
            return ["env", "shared"]
        if parts[1] == "env":
            if len(parts) == 2:
                return v["env"]
            eid = parts[2]
            if eid not in v["env"]:
                raise NotFound(path)                    # absent, not denied
            if len(parts) == 3:
                return ["tasks"]
            if parts[3] == "tasks":
                e = self.envs[eid]
                return [] if e.get("state") != "active" else list(e.get("tasks", []))
            raise NotFound(path)
        if parts[1] == "shared":
            if len(parts) == 2:
                return v["shared"]
            if parts[2] in self.shared:
                return self.shared[parts[2]]
        raise NotFound(path)
