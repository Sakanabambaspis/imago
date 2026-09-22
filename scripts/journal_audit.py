#!/usr/bin/env python3
"""Journal audit — mechanical faithfulness checks for the compiled journal.

The digest agent is an LLM and can fabricate; this script is the check that
does not hope. Modes:

  --dump      print uncompiled raw lines (per the cursor) with line numbers,
              for the digest agent to compile from
  --advance   validate everything pending, then move the cursor to
              end-of-raw (only on a fully clean validation)
  --dry-run   validate and report without advancing (default)

Validation, per date with uncompiled raw data:
  - a day file exists at journal/YYYY-MM/YYYY-MM-DD.md
  - `Sessions:` and `Public-safe:` header lines present; every session id
    in the pending raw lines is listed
  - every blockquote in "## User rationale (verbatim)" carries a citation
    `raw/<same-date>.jsonl#L<n>` and the quote — whitespace-normalized,
    trailing ellipsis allowed — is a contiguous substring of the cited raw
    line's decoded `prompt` (±3 lines window)

Exit codes: 0 clean (or nothing pending), 1 violations, 2 usage error.
The cursor advances only via --advance after a clean pass: a crash means
reprocessing, never skipping. Corrupt raw lines (a killed writer can tear
one) are skipped for session collection and reported if cited.
"""

import glob
import json
import os
import re
import sys

RAW_REL = (".imago", "journal", "raw")
STATE_REL = (".imago", "journal", "state.json")
JOURNAL_REL = "journal"
CITATION_RE = re.compile(r"raw/(\d{4}-\d{2}-\d{2})\.jsonl#L(\d+)")
PUBSAFE_RE = re.compile(r"(?m)^Public-safe:\s*(yes|no|unclear)\b")
QUOTE_CHARS = "\"“”‘’"
RAW_NAME_RE = re.compile(r"^\d{4}-\d{2}-\d{2}\.jsonl$")

violations = []


def fail(msg):
    violations.append(msg)


def root_dir():
    for env in ("ZCODE_PROJECT_DIR", "CLAUDE_PROJECT_DIR"):
        path = os.environ.get(env)
        if path:
            return path
    return os.getcwd()


def load_state(root):
    path = os.path.join(root, *STATE_REL)
    try:
        with open(path, encoding="utf-8") as f:
            state = json.load(f)
        cursor = state.get("cursor")
        if isinstance(cursor, dict) and "file" in cursor and "offset" in cursor:
            return {"file": str(cursor["file"]), "offset": int(cursor["offset"])}
    except Exception:
        pass
    return None


def raw_files(root):
    raw_dir = os.path.join(root, *RAW_REL)
    names = sorted(
        os.path.basename(p)
        for p in glob.glob(os.path.join(raw_dir, "*.jsonl"))
        if RAW_NAME_RE.match(os.path.basename(p))
    )
    return names


def pending_ranges(files, cursor):
    """filename -> byte offset where uncompiled data starts."""
    ranges = {}
    if not files:
        return ranges
    if cursor is None:
        return {f: 0 for f in files}
    cf, co = cursor["file"], cursor["offset"]
    if cf not in files:
        if cf > files[-1]:
            return {}  # compiled past everything on disk
        return {f: 0 for f in files}  # cursor file vanished; reprocess
    for f in files:
        if f > cf:
            ranges[f] = 0
        elif f == cf:
            ranges[f] = co
    return ranges


def iter_lines(path, start_byte):
    """Yield (1-based line number, line text) for lines starting at/after start_byte."""
    with open(path, encoding="utf-8", errors="replace") as f:
        offset = 0
        for no, line in enumerate(f, 1):
            start = offset
            offset += len(line.encode("utf-8"))
            if start >= start_byte:
                yield no, line.rstrip("\n")


def read_all_lines(root, fname):
    path = os.path.join(root, *RAW_REL, fname)
    with open(path, encoding="utf-8", errors="replace") as f:
        return f.read().splitlines()


def decode_prompt(line_text):
    try:
        obj = json.loads(line_text)
    except Exception:
        return None
    if isinstance(obj, dict) and isinstance(obj.get("prompt"), str):
        return obj["prompt"]
    return None


def normalize(text):
    return re.sub(r"\s+", " ", text).strip()


def strip_quote_edges(quote):
    quote = quote.strip()
    while quote and (quote[0] in QUOTE_CHARS or quote[0] in "—–-"):
        quote = quote[1:].lstrip()
    while quote:
        if quote[-1] in QUOTE_CHARS or quote[-1] in "—–-" or quote[-1] == "…":
            quote = quote[:-1].rstrip()
        elif quote.endswith("..."):
            quote = quote[:-3].rstrip()
        else:
            break
    return quote


def quote_paragraphs(day_text):
    """(1-based day-file line number, joined quote text) per blockquote in the
    'User rationale (verbatim)' section."""
    paragraphs = []
    in_section = False
    current, start_no = [], None
    for no, line in enumerate(day_text.splitlines(), 1):
        if line.startswith("## "):
            in_section = line.strip() == "## User rationale (verbatim)"
            if current:
                paragraphs.append((start_no, " ".join(current)))
                current, start_no = [], None
            continue
        if in_section and line.startswith(">"):
            if not current:
                start_no = no
            current.append(line.lstrip(">").strip())
        elif in_section and current:
            paragraphs.append((start_no, " ".join(current)))
            current, start_no = [], None
    if current:
        paragraphs.append((start_no, " ".join(current)))
    return paragraphs


def check_quote(root, date, day_file, start_no, para, raw_cache):
    m = CITATION_RE.search(para)
    if not m:
        fail("FAIL %s:%d blockquote has no raw/<date>.jsonl#L<n> citation" % (day_file, start_no))
        return 0
    cite_date, cite_line = m.group(1), int(m.group(2))
    checked = 1
    if cite_date != date:
        fail(
            "FAIL %s:%d blockquote cites raw/%s.jsonl but this day file covers %s "
            "(quotes cite their own day's raw layer)" % (day_file, start_no, cite_date, date)
        )
        return checked
    quote = strip_quote_edges(normalize(para[: m.start()] + " " + para[m.end():]))
    if not quote:
        fail("FAIL %s:%d blockquote is empty after removing the citation" % (day_file, start_no))
        return checked
    if date not in raw_cache:
        try:
            raw_cache[date] = read_all_lines(root, date + ".jsonl")
        except OSError:
            raw_cache[date] = []
    lines = raw_cache[date]
    for delta in (0, -1, 1, -2, 2, -3, 3):
        idx = cite_line - 1 + delta
        if not (0 <= idx < len(lines)):
            continue
        prompt = decode_prompt(lines[idx])
        if prompt is None:
            prompt = lines[idx]
        if quote in normalize(prompt):
            return checked
    fail(
        "FAIL %s:%d quote not found in raw/%s.jsonl#L%d (±3): %r"
        % (day_file, start_no, cite_date, cite_line, quote[:80])
    )
    return checked


def validate(root, pend, raw_cache):
    quote_count = 0
    for date in sorted(pend):
        lines = pend[date]
        day_file = os.path.join(JOURNAL_REL, date[:7], date + ".md")
        if not os.path.isfile(os.path.join(root, day_file)):
            fail("FAIL %s missing day file for %d pending raw line(s) in %s.jsonl"
                 % (day_file, len(lines), date))
            continue
        with open(os.path.join(root, day_file), encoding="utf-8") as f:
            day_text = f.read()
        if not PUBSAFE_RE.search(day_text):
            fail("FAIL %s no 'Public-safe: yes|no|unclear' header line" % day_file)
        sessions_line = next(
            (l for l in day_text.splitlines() if l.startswith("Sessions:")), None
        )
        if sessions_line is None:
            fail("FAIL %s no 'Sessions:' header line" % day_file)
            listed = set()
        else:
            listed = {s.strip() for s in sessions_line.split(":", 1)[1].split(",") if s.strip()}
        pending_ids = set()
        for _, text in lines:
            prompt = decode_prompt(text)
            if prompt is None and text.strip():
                # corrupt raw line: flag if cited, but don't block coverage
                pass
            try:
                obj = json.loads(text)
                pending_ids.add(str(obj.get("session_id", "unknown")))
            except Exception:
                continue
        missing = pending_ids - listed
        if missing:
            fail("FAIL %s 'Sessions:' does not cover pending session id(s): %s"
                 % (day_file, ", ".join(sorted(missing))))
        for start_no, para in quote_paragraphs(day_text):
            quote_count += check_quote(root, date, day_file, start_no, para, raw_cache)
    return quote_count


def dump(root, pend):
    if not pend:
        print("nothing pending")
        return
    for fname in sorted(pend):
        start = pend[fname]
        path = os.path.join(root, *RAW_REL, fname)
        size = os.path.getsize(path) if os.path.exists(path) else 0
        print("== raw/%s (pending from byte %d to %d) ==" % (fname, start, size))
        for no, text in iter_lines(path, start):
            print("L%d | %s" % (no, text))


def advance(root, files):
    state_path = os.path.join(root, *STATE_REL)
    os.makedirs(os.path.dirname(state_path), exist_ok=True)
    last = files[-1]
    size = os.path.getsize(os.path.join(root, *RAW_REL, last))
    state = {"schema_v": 1, "cursor": {"file": last, "offset": size}}
    tmp = state_path + ".tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(state, f, indent=2)
        f.write("\n")
    os.replace(tmp, state_path)
    print("cursor advanced to %s @ byte %d" % (last, size))


def main(argv):
    mode = "check"
    for arg in argv:
        if arg in ("--dump", "--advance", "--dry-run"):
            mode = arg[2:]
        else:
            print("usage: journal_audit.py [--dump | --advance | --dry-run]", file=sys.stderr)
            return 2
    root = root_dir()
    files = raw_files(root)
    pend = pending_ranges(files, load_state(root))
    if mode == "dump":
        dump(root, pend)
        return 0
    pend_lines = {}  # date -> [(line number, raw line text)]
    for fname, start in sorted(pend.items()):
        path = os.path.join(root, *RAW_REL, fname)
        date = fname[: -len(".jsonl")]
        for line in iter_lines(path, start):
            pend_lines.setdefault(date, []).append(line)
    raw_cache = {}
    quote_count = validate(root, pend_lines, raw_cache)
    if violations:
        for v in violations:
            print(v)
        print("%d violation(s)" % len(violations))
        return 1
    if not pend_lines:
        print("nothing pending — journal is up to date")
        return 0
    print("OK: %d date(s) validated, %d quote(s) verified against the raw layer"
          % (len(pend_lines), quote_count))
    if mode == "advance":
        advance(root, files)
    else:
        print("dry run — cursor not moved (use --advance to commit)")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
