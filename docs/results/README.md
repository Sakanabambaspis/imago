# Results notes

Wave JSONs land here from `imago eval p1|p2`. The first real deliverable
(design-mvp §2, criterion 3) is a **baseline wave** (plain loop) and a
**countermeasure wave** (stance loop) over the same seeds/topics, with the
delta written up as this project's first result note.

```bash
export IMAGO_API_KEY=...
imago eval p1 --wave pilot --loop plain    # baseline arm
imago eval p1 --wave pilot --loop stance   # countermeasure arm
```

Wave JSONs from stub runs are scorer self-tests, not results — delete them.
Pilot-sized waves (40 runs) are provisional by construction; the corpus rule
is ≥100 runs per wave for reportable confidence intervals (run
`imago eval p1 --wave full` when the delta justifies the spend).
