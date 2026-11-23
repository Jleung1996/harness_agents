#!/usr/bin/env python3
"""
split_skill_bundle.py

Rebuilds individual SKILL.md and references/*.md files from a bundled master
markdown file (skill-bundle-master.md).

The bundle wraps every file like this:

    ===== BEGIN FILE 7/55 =====
    SKILL: python-pro
    PATH: skills/python-pro/references/testing.md
    BYTES: 10324
    BYTES_LF: 10173
    LINES: 404
    EOL: CRLF
    ===== BEGIN CONTENT =====
    ...verbatim file content...
    ===== END CONTENT =====
    ===== END FILE 7/55 =====

Usage:
    python split_skill_bundle.py --bundle skill-bundle-master.md --dest skills

    # overwrite an existing destination
    python split_skill_bundle.py --bundle skill-bundle-master.md --dest skills --force

    # dry run: parse and report, write nothing
    python split_skill_bundle.py --bundle skill-bundle-master.md --dest skills --dry-run

Exit codes:
    0  every block parsed and every file matched its declared byte count
    1  parse failure or byte-count mismatch (nothing is silently half-written)
    2  bad usage / destination exists without --force
"""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

BEGIN_FILE = re.compile(r"^===== BEGIN FILE (\d+)/(\d+) =====$")
END_FILE = re.compile(r"^===== END FILE (\d+)/(\d+) =====$")
META_LINE = re.compile(r"^([A-Z_]+): (.*)$")
DECLARED_FILES = re.compile(r"\*\*Files:\*\* (\d+)")
DECLARED_BYTES = re.compile(r"\*\*Total bytes:\*\* (\d+)")

BEGIN_CONTENT = "===== BEGIN CONTENT ====="
END_CONTENT = "===== END CONTENT ====="


class BundleError(Exception):
    pass


def parse_blocks(text: str) -> list[dict]:
    """Parse the bundle into a list of {meta, body} dicts. Raises on malformed input."""
    blocks: list[dict] = []
    state = "idle"
    meta: dict[str, str] = {}
    body: list[str] = []

    for lineno, line in enumerate(text.split("\n"), start=1):
        m = BEGIN_FILE.match(line)
        if m:
            state, meta, body = "header", {"ordinal": m.group(1), "of": m.group(2)}, []
            continue

        if line == BEGIN_CONTENT:
            # Only meaningful directly after a BEGIN FILE header. The bundle's PART 0
            # contains an illustrative example that also prints this line, so ignore
            # stray occurrences rather than failing on them.
            if state == "header":
                state = "body"
            continue

        if line == END_CONTENT:
            if state == "body":
                state = "after"
            continue

        m = END_FILE.match(line)
        if m:
            if state != "after":
                raise BundleError(
                    f"block {meta.get('ordinal', '?')}: END FILE without END CONTENT"
                )
            if "PATH" not in meta:
                raise BundleError(f"block {meta['ordinal']}: missing PATH header")
            blocks.append({"meta": meta, "body": "\n".join(body)})
            state = "idle"
            continue

        if state == "header":
            mm = META_LINE.match(line)
            if mm:
                meta[mm.group(1)] = mm.group(2)
        elif state == "body":
            body.append(line)

    return blocks


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(
        description="Rebuild individual skill files from a bundled master markdown file."
    )
    ap.add_argument("--bundle", required=True, type=Path, help="path to skill-bundle-master.md")
    ap.add_argument("--dest", required=True, type=Path, help="directory to write skills/ into")
    ap.add_argument("--force", action="store_true", help="overwrite a non-empty destination")
    ap.add_argument("--dry-run", action="store_true", help="parse and verify, write nothing")
    args = ap.parse_args(argv)

    if not args.bundle.is_file():
        print(f"ERROR: bundle not found: {args.bundle}", file=sys.stderr)
        return 2

    if args.dest.exists() and not args.force and not args.dry_run:
        existing = sum(1 for p in args.dest.rglob("*") if p.is_file())
        if existing:
            print(
                f"ERROR: destination already has {existing} file(s): {args.dest}\n"
                f"       re-run with --force to overwrite",
                file=sys.stderr,
            )
            return 2

    raw = args.bundle.read_bytes()
    try:
        text = raw.decode("utf-8-sig")
    except UnicodeDecodeError as exc:
        print(f"ERROR: bundle is not valid UTF-8: {exc}", file=sys.stderr)
        return 1

    # Normalise any CRLF/CR in the bundle itself; per-file EOLs are restored below.
    text = text.replace("\r\n", "\n").replace("\r", "\n")

    try:
        blocks = parse_blocks(text)
    except BundleError as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1

    if not blocks:
        print("ERROR: no file blocks found - is this the right bundle?", file=sys.stderr)
        return 1

    declared_files_m = DECLARED_FILES.search(text)
    declared_bytes_m = DECLARED_BYTES.search(text)
    declared_files = int(declared_files_m.group(1)) if declared_files_m else None
    declared_bytes = int(declared_bytes_m.group(1)) if declared_bytes_m else None

    problems: list[str] = []
    written = 0
    total_bytes = 0
    per_skill: dict[str, int] = {}

    for blk in blocks:
        meta = blk["meta"]
        body = blk["body"]

        rel = meta["PATH"]
        if rel.startswith("skills/"):
            rel = rel[len("skills/"):]

        eol = meta.get("EOL", "LF")
        if eol == "CRLF":
            out_text = body.replace("\n", "\r\n")
        else:
            out_text = body
        out_bytes = out_text.encode("utf-8")

        expected_bytes = int(meta["BYTES"]) if "BYTES" in meta else None
        if expected_bytes is not None and len(out_bytes) != expected_bytes:
            problems.append(
                f"{rel}: BYTES off (expected {expected_bytes}, got {len(out_bytes)})"
            )

        expected_lines = int(meta["LINES"]) if "LINES" in meta else None
        if expected_lines is not None:
            actual_lines = body.count("\n") + (0 if body.endswith("\n") else 1)
            if body == "":
                actual_lines = 0
            if actual_lines != expected_lines:
                problems.append(
                    f"{rel}: LINES off (expected {expected_lines}, got {actual_lines})"
                )

        if not args.dry_run:
            target = args.dest / rel
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_bytes(out_bytes)

        written += 1
        total_bytes += len(out_bytes)
        skill = rel.split("/")[0]
        per_skill[skill] = per_skill.get(skill, 0) + 1

    print()
    print(f"Bundle : {args.bundle}")
    print(f"Dest   : {'(dry run, nothing written)' if args.dry_run else args.dest}")
    print(
        f"Files  : {written}"
        + (f" (declared in bundle: {declared_files})" if declared_files is not None else "")
    )
    print(
        f"Bytes  : {total_bytes}"
        + (f" (declared in bundle: {declared_bytes})" if declared_bytes is not None else "")
    )
    print()
    for skill in sorted(per_skill):
        print(f"  {skill:<32} {per_skill[skill]:>3} file(s)")
    print()

    failed = False

    if declared_files is not None and written != declared_files:
        print(
            f"MISMATCH: bundle declares {declared_files} files but {written} were parsed.",
            file=sys.stderr,
        )
        failed = True

    if declared_bytes is not None and total_bytes != declared_bytes:
        print(
            f"MISMATCH: bundle declares {declared_bytes} bytes but {total_bytes} were produced.",
            file=sys.stderr,
        )
        failed = True

    if problems:
        print(f"{len(problems)} integrity problem(s):", file=sys.stderr)
        for p in problems:
            print(f"  - {p}", file=sys.stderr)
        failed = True

    if failed:
        return 1

    print("All blocks parsed; every file matches its declared byte count." if not args.dry_run
          else "All blocks parsed; every file matches its declared byte count (dry run).")
    return 0


if __name__ == "__main__":
    sys.exit(main())
