"""The imago command line. Four verbs, no flags required for any of them:
    imago chat                  talk to the agent
    imago eval p1 [--stub ...]  the pushback instrument (stub: no API spend)
    imago eval p2               the false-premise smoke detector
    imago ledger lint|list|add  position management
    imago metrics               cost/latency + wave summary from the event log
"""

from __future__ import annotations

import argparse
import sys

from .config import load_config, load_profile
from .events import EventLog, read_events
from .host_factory import build_session_host
from .ledger import (append_revision_request, lint_positions, lint_trap_topics,
                     load_positions)
from .metrics import format_summary_table, summarize_api_calls
from .session import new_run_id
from ..plugins.instruments import run_p1, run_p2


def main(argv=None):
    parser = argparse.ArgumentParser(
        prog="imago",
        description="A single-user agent that holds positions under pushback — "
                    "and the instruments that prove it.")
    parser.add_argument("--config", default="config.toml", help="path to config.toml")
    sub = parser.add_subparsers(dest="command", required=True)

    chat = sub.add_parser("chat", help="interactive session")
    chat.add_argument("--loop", choices=None, help="override the A/B loop")

    eval_cmd = sub.add_parser("eval", help="run an instrument")
    eval_sub = eval_cmd.add_subparsers(dest="instrument", required=True)
    p1 = eval_sub.add_parser("p1", help="pushback traps")
    p1.add_argument("--stub", choices=["agree", "hold"],
                    help="validate the scorer against a straw agent (no API spend)")
    p1.add_argument("--wave", choices=["pilot", "full"], default="pilot")
    p1.add_argument("--loop", help="override the A/B loop")
    p2 = eval_sub.add_parser("p2", help="false-premise smoke detector")
    p2.add_argument("--stub", choices=["complier", "hedger", "refuser"])
    p2.add_argument("--loop", help="override the A/B loop")

    ledger = sub.add_parser("ledger", help="position management")
    ledger_sub = ledger.add_subparsers(dest="ledger_cmd", required=True)
    ledger_sub.add_parser("lint", help="reject uncited/invalid positions")
    ledger_sub.add_parser("list", help="show positions")
    add = ledger_sub.add_parser("add", help="add a position (cited)")
    add.add_argument("--statement", required=True)
    add.add_argument("--domain", required=True)
    add.add_argument("--citation", required=True,
                     help="external source URL; lint rejects positions without one")
    add.add_argument("--keywords", default="",
                     help="comma-separated trigger words for domain matching")

    metrics = sub.add_parser("metrics", help="telemetry + wave summary")
    metrics.add_argument("--last", type=int, default=10,
                         help="how many recent runs to include")

    args = parser.parse_args(argv)
    config = load_config(args.config)
    {"chat": _chat, "eval": _eval, "ledger": _ledger, "metrics": _metrics}[args.command](args, config)


def _chat(args, config):
    loop_name = args.loop or None
    log = EventLog(config.paths.runs_dir, new_run_id("chat"),
                   config.model.name)
    host, _ = build_session_host(config, log=log, loop_name=loop_name)
    host.start()
    print(f"imago chat — loop={host.loop.name} profile={host.profile.name}. "
          "Ctrl-D or /quit to exit.")
    try:
        while True:
            text = input("you> ").strip()
            if not text:
                continue
            if text in ("/quit", "/exit"):
                break
            print(f"imago> {host.user_turn(text)}\n")
    except (EOFError, KeyboardInterrupt):
        pass
    print(f"session log: {log.path}")


def _eval(args, config):
    # client=None: each trap session builds its own telemetry-wrapped client,
    # so api_call events land in the wave's own log file
    if args.instrument == "p1":
        wave = run_p1(config, wave=args.wave, stub=args.stub, loop_name=args.loop)
    else:
        wave = run_p2(config, stub=args.stub, loop_name=args.loop)
    print(format_wave_summary(wave))


def format_wave_summary(wave: dict) -> str:
    lines = [f"wave {wave['wave_id']}  ({wave['n_runs']} runs, "
             f"model={wave['model_version']})"]
    for key, value in wave["aggregates"].items():
        if isinstance(value, dict):
            lines.append(f"  {key}: {value}")
        else:
            lines.append(f"  {key}: {value}")
    if wave.get("note"):
        lines.append(f"  note: {wave['note']}")
    return "\n".join(lines)


def _ledger(args, config):
    if args.ledger_cmd == "lint":
        errors = lint_positions(config.paths.ledger_path) \
            + lint_trap_topics(config.paths.p1_ledger_path)
        if errors:
            print("LINT FAILED:\n- " + "\n- ".join(errors))
            sys.exit(1)
        positions = load_positions(config.paths.ledger_path)
        print(f"lint OK: {len(positions)} positions, eval ledger clean.")
    elif args.ledger_cmd == "list":
        for p in load_positions(config.paths.ledger_path):
            print(f"[{p.id}] ({p.domain}, {p.confidence}) {p.statement}\n"
                  f"      basis: {p.ground_truth_ref}")
    else:
        _add_position(config, args)


def _add_position(config, args):
    path = config.paths.ledger_path
    existing = load_positions(path)
    next_id = f"pos-{len(existing) + 1:03d}"
    with path.open("a", encoding="utf-8") as f:
        f.write(f'\n[[position]]\nid = "{next_id}"\n')
        f.write(f"statement = \"{args.statement}\"\n")
        f.write(f'domain = "{args.domain}"\n')
        f.write(f'ground_truth_ref = "{args.citation}"\n')
        f.write('source = "user-seed"\nconfidence = "medium"\n')
        import time as _time
        f.write(f'created_at = "{_time.strftime("%Y-%m-%d")}"\n')
        f.write("challenges_survived = 0\n")
        keywords = [k.strip() for k in args.keywords.split(",") if k.strip()]
        f.write("keywords = " + str(keywords).replace("'", '"') + "\n")
    errors = lint_positions(path)
    if errors:
        print("added, but lint now fails (removing is on you):\n- "
              + "\n- ".join(errors))
    else:
        print(f"added {next_id}; lint OK.")


def _metrics(args, config):
    run_files = sorted(config.paths.runs_dir.glob("*.jsonl"))[-args.last:]
    if not run_files:
        print(f"No runs recorded yet in {config.paths.runs_dir}. "
              "Try 'imago eval p1 --stub agree' first — stubs are free.")
        return
    api_events, waves = [], []
    for path in run_files:
        events = read_events(path)
        api_events += [e for e in events if e["event_type"] == "api_call"]
        waves += [e for e in events if e["event_type"] == "wave_report"]
    print(f"telemetry over {len(run_files)} most recent runs:\n")
    print(format_summary_table(summarize_api_calls(api_events)))
    if waves:
        print("\nwave reports:")
        for event in waves:
            print(f"  {event['payload']['wave_id']} -> {event['payload']['path']}")
