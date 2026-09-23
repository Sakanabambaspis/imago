"""Entry point: `python -m playground` — the R&D REPL.

    python -m playground <name> [--config path]   create or resume a session
    python -m playground --list                   list known sessions

Run from the repo root: sessions live under the config's runs_dir, same as
`imago` itself. A turn is recorded as a `playground_user` event before the
call and a `playground_reply` event after, so resume replays the real
conversation — including hold-rewrites the stance loop substitutes for the
draft — from the session's own event log.
"""

from __future__ import annotations

import argparse
from pathlib import Path

from imago.core.config import load_config, load_dotenv

from .sessions import list_sessions, open_session, turn


def main(argv=None):
    load_dotenv()
    parser = argparse.ArgumentParser(
        prog="playground",
        description="R&D chat over the product's SessionHost — named, "
                    "resumable sessions; the product never imports this.")
    parser.add_argument("name", nargs="?",
                        help="session name: letters, digits, '_', '-'")
    parser.add_argument("--config", default="config.toml",
                        help="path to config.toml (creation only; resume "
                             "uses the session's stored config)")
    parser.add_argument("--list", action="store_true",
                        help="list known sessions and exit")
    args = parser.parse_args(argv)

    config = load_config(args.config)
    if args.list:
        rows = list_sessions(config)
        if not rows:
            print(f"No sessions yet in {config.paths.runs_dir}.")
            return
        for name, config_path, created, turns in rows:
            print(f"{name:<20} turns={turns:<4} "
                  f"config={Path(config_path).name:<18} created={created}")
        return
    if not args.name:
        parser.error("a session name is required (or pass --list)")

    host, log, action = open_session(args.name, config, args.config)
    where = ("new session" if action == "created"
             else f"resumed, {host.turn} turn(s) of history")
    print(f"playground '{args.name}' — loop={host.loop.name} "
          f"profile={host.profile.name} ({where}). Ctrl-D or /quit to exit.")
    try:
        while True:
            text = input("you> ").strip()
            if not text:
                continue
            if text in ("/quit", "/exit"):
                break
            reply = turn(host, log, text)
            print(f"imago> {reply}\n")
    except (EOFError, KeyboardInterrupt):
        pass
    print(f"session log: {log.path}")


if __name__ == "__main__":
    main()
