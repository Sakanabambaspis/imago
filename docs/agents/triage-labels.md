# Triage Labels

The skills speak in terms of five canonical triage roles. This file maps those roles to the actual label strings used in this repo's issue tracker.

| Label in mattpocock/skills | Label in our tracker | Meaning                                  |
| -------------------------- | -------------------- | ---------------------------------------- |
| `needs-triage`             | `needs-triage`       | Maintainer needs to evaluate this issue  |
| `needs-info`               | `needs-info`         | Waiting on reporter for more information |
| `ready-for-agent`          | `ready-for-agent`    | Fully specified, ready for an AFK agent  |
| `ready-for-human`          | `ready-for-human`    | Requires human implementation            |
| `wontfix`                  | `wontfix`            | Will not be actioned                     |

When a skill mentions a role (e.g. "apply the AFK-ready triage label"), use the corresponding label string from this table.

Edit the right-hand column to match whatever vocabulary you actually use.

In this repo the labels are GitHub labels on `Sakanabambaspis/imago`, applied
via `gh issue edit <n> --add-label "<label>"` (see `issue-tracker.md`).

**Binding condition:** `ready-for-agent` may only be applied per the rubric
and consent rules in [`agent-ready.md`](agent-ready.md) — evidence-cited
checklist, quote-back approval, named override. `wontfix` (rejected
enhancements) also requires a `.out-of-scope/` record per the triage skill.
