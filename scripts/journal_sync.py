#!/usr/bin/env python3
"""Journal sync — commit and push journal/ to its private cloud remote.

Reads `.zcode/journal-sync.json`: {"remote": <url>, "branch": "main"}.

- Unconfigured (missing file or empty remote): documented no-op with a loud
  warning, exit 0 — the pipeline runs cloud-less until the owner creates the
  private repo and drops the URL in.
- Configured: `journal/` is its own git repo (independent history so the
  journal can be published later without exposing Imago code). This script
  inits it on first use, sets `origin`, commits pending changes as
  `journal: <YYYY-MM-DD> digest`, and pushes. Never force-pushes; a
  diverged remote fails loudly (exit 1) for manual resolution.

The config holds a URL only — no tokens; auth comes from the owner's
existing git credential helper or SSH key.
"""

import json
import os
import subprocess
import sys
from datetime import datetime

CONFIG_REL = (".zcode", "journal-sync.json")
JOURNAL_REL = "journal"


def root_dir():
    for env in ("ZCODE_PROJECT_DIR", "CLAUDE_PROJECT_DIR"):
        path = os.environ.get(env)
        if path:
            return path
    return os.getcwd()


def load_config(root):
    path = os.path.join(root, *CONFIG_REL)
    try:
        with open(path, encoding="utf-8") as f:
            cfg = json.load(f)
    except FileNotFoundError:
        return None, "no config at .zcode/journal-sync.json"
    except Exception as exc:
        return None, "config unreadable (%s)" % exc
    remote = cfg.get("remote")
    if not remote:
        return None, "config has no 'remote' yet"
    return {"remote": remote, "branch": cfg.get("branch", "main")}, None


def git(journal, *args, check=True):
    result = subprocess.run(
        ["git", "-C", journal, *args],
        capture_output=True, text=True,
    )
    if check and result.returncode != 0:
        sys.stderr.write(result.stderr)
        raise SystemExit("journal_sync: git %s failed (exit %d)" % (args[0], result.returncode))
    return result


def main(argv):
    dry_run = "--dry-run" in argv
    root = root_dir()
    journal = os.path.join(root, JOURNAL_REL)
    cfg, why = load_config(root)
    if cfg is None:
        print("journal_sync: NO-OP — %s." % why)
        print("journal_sync: the compiled journal is NOT leaving this machine.")
        print("journal_sync: create a PRIVATE GitHub repo and put {\"remote\": \"<url>\", \"branch\": \"main\"} into .zcode/journal-sync.json")
        return 0
    branch = cfg["branch"]

    if not os.path.isdir(journal):
        raise SystemExit("journal_sync: %s does not exist — nothing to sync" % journal)

    if dry_run:
        has_git = os.path.isdir(os.path.join(journal, ".git"))
        print("journal_sync: DRY RUN — remote=%s branch=%s repo=%s" % (cfg["remote"], branch, "exists" if has_git else "will be initialized"))
        return 0

    result = git(journal, "rev-parse", "--git-dir", check=False)
    if result.returncode != 0:
        print("journal_sync: initializing journal repo on branch %s" % branch)
        init = git(journal, "init", "-b", branch, check=False)
        if init.returncode != 0:  # git < 2.28 has no -b
            git(journal, "init")
            git(journal, "symbolic-ref", "HEAD", "refs/heads/%s" % branch)

    remotes = git(journal, "remote").stdout.split()
    current_url = git(journal, "remote", "get-url", "origin", check=False).stdout.strip()
    if current_url != cfg["remote"]:
        if "origin" in remotes:
            git(journal, "remote", "set-url", "origin", cfg["remote"])
            print("journal_sync: origin URL updated")
        else:
            git(journal, "remote", "add", "origin", cfg["remote"])
            print("journal_sync: origin set to %s" % cfg["remote"])

    git(journal, "add", "-A")
    if git(journal, "diff", "--cached", "--quiet", check=False).returncode == 0:
        print("journal_sync: nothing new to commit")
    else:
        msg = "journal: %s digest" % datetime.now().strftime("%Y-%m-%d")
        git(journal, "commit", "-m", msg)
        print("journal_sync: committed %s" % msg)

    push = git(journal, "push", "-u", "origin", branch, check=False)
    if push.returncode != 0:
        sys.stderr.write(push.stderr)
        raise SystemExit(
            "journal_sync: push FAILED — the remote diverged or auth failed. "
            "This script never force-pushes; inspect manually."
        )
    print("journal_sync: pushed %s to origin" % branch)
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
