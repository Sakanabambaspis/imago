# Agent-ready gate

What `ready-for-agent` means, what evidence licenses it, and what counts as
human consent. The triage skill and any agent applying or acting on the label
are bound by this file.

The principle is the project's own, applied to its development process:
a state transition is a position change, and position changes require
evidence — insistence, enthusiasm, and social pressure never produce one.

## Readiness rubric

A ticket may carry `ready-for-agent` only when **every** item holds, and the
labeling record (issue comment or body) cites the evidence per item:

1. **Executable acceptance criteria.** Each criterion is a command, an
   observable behavior, or a test that can pass or fail — never prose like
   "works correctly". An agent must be able to falsify every line.
2. **One success command.** A single command (or short sequence) an AFK agent
   runs to know it is done — e.g. `pytest tests/test_judge_client.py` or
   `imago eval p1 --stub agree`. This repo's existing culture: stubs before
   spend, lint before run.
3. **Zero open design decisions.** No "TBD", "or maybe", "agent's choice" on
   anything semantic. Open questions are resolved by grilling first; the
   resolution is linked (comment, ADR, `CONTEXT.md`).
4. **Verified claim.** Bugs: reproduced by someone who ran the steps, with the
   output recorded (triage step 3). Enhancements: the redundancy and
   prior-rejection checks were run, and the claim survived them.
5. **Bounded blast radius.** The areas touched are named; applicable ADRs are
   listed; nothing on the list is contradicted silently.
6. **No spend, or budgeted spend.** Real-model runs and paid API calls are
   out of scope for the ticket unless the maintainer approved a budget in
   writing on the ticket. Humans authorize spend; agents execute it.
7. **One context window.** The ticket is completable AFK in a single fresh
   session. Bigger means it is mis-ticketed — split it.

Missing any item → the ticket stays at `needs-triage` (or returns to it), with
a comment naming the missing items. An agent may *draft* the evidence, but see
the consent rules below for who can convert a draft into the label.

## Consent rules (what counts as human approval)

These exist because the failure mode is not the agent disobeying — it is the
agent *misreading* a human as having verified something they did not.

1. **Quote-back, then affirmative.** Before applying `ready-for-agent`, the
   agent posts the rubric checklist with per-item evidence. Approval must
   reference that artifact and name the ticket: "approve #42 as listed" or
   "approved as a set: #3 #4 #5". A bare "ok", "sounds good", "👍", approval
   of a different artifact, or an answer to a different question does **not**
   authorize the transition. Silence does not authorize anything.
2. **Named override only.** A quick override ("move #42 to ready-for-agent")
   is honored when it is an imperative naming the ticket number. It is never
   inferred from general praise of other work, never extended to tickets not
   named, and never applied retroactively to a batch.
3. **Structure approval ≠ readiness.** Approving a `/to-tickets` breakdown
   approves granularity and blocking edges only. Tickets from a fresh
   breakdown ship as `needs-triage`; the triage pass (rubric + quote-back)
   promotes them. Exception: if the maintainer explicitly says the batch is
   pre-verified ("publish these as ready"), say so in the record and apply.
4. **The human can skip the ritual — by saying so, once per batch.** The
   point of this file is not ceremony; it is that shortcuts happen on the
   record, in words, instead of by inference.

## Pickup gate (enforcement at the moment it matters)

Label-time rules leak; pickup-time rules don't. Any agent asked to implement
a ticket — via `/implement` or otherwise — **first** verifies, mechanically:

- [ ] the ticket carries `ready-for-agent`;
- [ ] acceptance criteria exist and are executable as written;
- [ ] no open-decision markers (`TBD`, "agent's choice", unresolved questions
      in comments);
- [ ] the success command is present and actually runs green *before* starting
      (it is also the finish line);
- [ ] blast radius matches what the ticket declared.

Any failure → **stop and report**; do not improvise, do not "just do it
anyway", do not relabel. The agent's move is back to the maintainer, not
forward into the code.

This gate also makes grandfathering safe: tickets labeled before this file
exists (the 2026-09-24 migration import) do not need mass re-triage — the
gate above is what actually stops an unready ticket from consuming work.
