-- Instrument the choke point, not the call sites.
-- When many programs write one table, a guard placed in each program misses the next one written.
-- These SQLite triggers put the guard on the table itself.

-- 1) A lifecycle log that cannot be skipped: every REAL status change is recorded, whoever made it.
--    (Measured in my own system: only 5% of task status changes had a log row before this.)
CREATE TABLE IF NOT EXISTS tasks (id INTEGER PRIMARY KEY, title TEXT, status TEXT);
CREATE TABLE IF NOT EXISTS task_events (id INTEGER PRIMARY KEY AUTOINCREMENT, ts TEXT, task_id INTEGER,
                                        from_state TEXT, to_state TEXT, actor TEXT);
CREATE TRIGGER IF NOT EXISTS trg_task_lifecycle AFTER UPDATE OF status ON tasks
WHEN OLD.status IS NOT NEW.status
BEGIN
  INSERT INTO task_events(ts, task_id, from_state, to_state, actor)
  VALUES (strftime('%Y-%m-%dT%H:%M:%f','now'), NEW.id, OLD.status, NEW.status, 'db_trigger');
END;

-- 2) An intake cap paced to execution: when the undecided backlog reaches its cap, a new proposal is
--    IGNORED and the refusal is LOGGED (never silent). A scheduled job rewrites the cap from measured
--    throughput, e.g. max(25, 2 x tasks completed per week).
CREATE TABLE IF NOT EXISTS proposals (id INTEGER PRIMARY KEY, title TEXT, status TEXT DEFAULT 'pending');
CREATE TABLE IF NOT EXISTS caps (tbl TEXT PRIMARY KEY, cap INTEGER NOT NULL);
CREATE TABLE IF NOT EXISTS rejections (id INTEGER PRIMARY KEY AUTOINCREMENT, ts TEXT, tbl TEXT, open_n INTEGER, cap INTEGER);
CREATE TRIGGER IF NOT EXISTS trg_proposal_cap BEFORE INSERT ON proposals
WHEN (SELECT COUNT(*) FROM proposals WHERE status = 'pending') >= COALESCE((SELECT cap FROM caps WHERE tbl='proposals'), 1000000000)
BEGIN
  INSERT INTO rejections(ts, tbl, open_n, cap)
  VALUES (strftime('%Y-%m-%dT%H:%M:%S','now'), 'proposals',
          (SELECT COUNT(*) FROM proposals WHERE status='pending'), (SELECT cap FROM caps WHERE tbl='proposals'));
  SELECT RAISE(IGNORE);   -- the log row above is kept: RAISE(IGNORE) does not roll back earlier trigger steps
END;
