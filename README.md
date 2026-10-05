# Nohvara: notes and components from a self-driving operating layer

I'm Morris Javan Andanje, based in Nairobi. I work on one problem: **protecting creative capacity**.
Creative people and creative businesses lose too much time and attention to fragmented systems,
repetitive decisions and operational work. Where decisions or processes repeat, I turn them into rules,
systems and automation, so human attention goes where it matters.

**Nohvara** is the system I build to do that for my own work first. It's an operating layer of software agents,
loops and learners that runs my ventures from one laptop, a small rented server and a phone. This repository holds
self-contained pieces of it, rewritten to stand alone, with tests. It shows the method, not the private system:
no personal data, client material or credentials are here.

## The method in four rules

1. **A mechanism that runs but concludes nothing is a failure, not a success.** Every scheduled job has to say what
   it changed (`CHANGED`, `NO-CHANGE` or `UNMEASURED`), and "unmeasured" is never shown as zero.
2. **Verify at the endpoint, not the exit code.** A backup counts only when the remote copy checks out, and a
   submission counts only when the confirmation arrives.
3. **Instrument the choke point, not the call sites.** When 14 programs write to one table, the guard lives on the
   table.
4. **Learn hierarchically, never from one flat pool.** Thin evidence borrows from the wider system; strong evidence
   keeps its own voice.

## What's in here

| Folder | What it is | The lesson behind it |
|---|---|---|
| [`pooling/`](pooling) | Empirical-Bayes partial pooling of success rates | One flat pool dragged a 3-observation unit from 67% to 46% toward a population it didn't belong to; pooling within the right branch fixed it |
| [`ideas/`](ideas) | An idea warehouse classifier: pre-registered tests, a Beta belief, validated / refuted / inconclusive | Of 2,153 ideas in my own system, **none had ever been tested against reality**. Untested isn't refuted, and declined isn't refuted |
| [`namespace/`](namespace) | A Plan 9-style resolver: each environment sees only its own subtree plus shared resources | The boundary is "not found", never "access denied" |
| [`patterns/`](patterns) | SQLite triggers: a lifecycle log at the table, and an intake cap paced to throughput | Only 5% of task status changes were being logged; a trigger at the table made it 100% |
| [`packages/nohvara-paths`](packages/nohvara-paths) | The project-root lookup copied into 765 modules, as one versioned package | Installed on another machine with `pip --require-hashes`; a tampered hash is refused |

## Some measured outcomes from running this on myself

- **Work that looked healthy wasn't.** 8 of 20 scheduled jobs had been dead for months while every run was recorded
  as a success. 170 of 187 processes registered as "loops" had no control variable, setpoint or period.
- **An offsite backup over a slow link.** The backup had been stale for 26.9 days, and a full copy of a 725 MB database
  can't cross a 0.08 MB/s uplink in time. Shipping only changed pages (`sqlite3_rsync`) syncs it in 34 seconds with
  1.9 MB.
- **Ideas paced to execution.** About 57 new proposals a week against 58 completed tasks: the problem was the stock of
  1,000+ undecided ideas, not the inflow. Undecided ideas now go back to a warehouse, and intake is capped by measured
  throughput.

## Running the tests

```bash
python -m pytest tests/        # or: python tests/run_all.py
```

Everything here uses only the Python standard library (3.10+).

## Contact

LinkedIn: [morris-javan-andanje](https://www.linkedin.com/in/morris-javan-andanje) · GitHub: [sirromnavaj](https://github.com/sirromnavaj)
