#!/usr/bin/env python3
"""Documentation repetition detector (Prevention gate for the boilerplate-audit epic).

Flags generator-produced boilerplate: non-trivial prose lines repeated within a
single Markdown page. Two severities (guardrail #5):

* ERROR  -- a repeated line matches a known boilerplate *marker* (see
            ``scripts/repetition-markers.txt``). These are scaffold phrases that
            should never survive remediation. ERRORs fail CI (exit code 1).
* WARN   -- any other significant line repeated ``>= threshold`` times. Reported
            as evidence but does NOT fail CI, so legitimate-but-repetitive prose
            in other contributors' in-flight PRs is surfaced without blocking.

Guardrails implemented (see epic yeongseon/azure-container-apps-practical-guide#376):
  1. YAML frontmatter (the leading ``---`` ... ``---`` block) is excluded, so
     repeated ``source:`` / ``based_on`` / ``mslearn_url`` keys are never counted.
  2. Fenced code blocks (``` ``` ``` and ``~~~``) are skipped, so repeated CLI /
     KQL lines are not treated as prose.
  3. Because KQL lives inside fences, ``| where`` / ``| summarize`` pipe lines are
     never reached; as defense in depth, Markdown table rows (lines starting with
     ``|``) are also skipped.
  4. Per-repo path differences are handled by scanning whatever roots are passed on
     the command line (default ``docs``); repos lacking ``docs/best-practices/``
     simply contribute fewer files.
  5. Marker hits are ERROR; generic repetition is WARN (this module).
  6. A per-repo allowlist file (``scripts/repetition-allowlist.txt``) exempts
     legitimate repeated lines by exact stripped text.
  7. Output is actionable: file path, the offending line, its repeat count, and the
     1-based line numbers where it occurs -- not just totals.

Usage:
    python3 scripts/detect_repetition.py [PATHS ...]
        [--threshold N] [--min-length N]
        [--markers-file FILE] [--allowlist FILE]

Exit code is 1 if any ERROR (marker) is found, else 0.
"""

from __future__ import annotations

import argparse
import os
import sys
from collections import defaultdict


DEFAULT_THRESHOLD = 3
DEFAULT_MIN_LENGTH = 40
DEFAULT_MARKERS_FILE = os.path.join(
    os.path.dirname(os.path.abspath(__file__)), "repetition-markers.txt"
)
DEFAULT_ALLOWLIST_FILE = os.path.join(
    os.path.dirname(os.path.abspath(__file__)), "repetition-allowlist.txt"
)


def significant_lines(text, min_length=DEFAULT_MIN_LENGTH):
    """Yield ``(lineno, stripped_text)`` for prose lines worth counting.

    Frontmatter, fenced code, blank lines, headings, table rows, and short lines
    are all excluded.

    A leading frontmatter block is skipped:

    >>> doc = '---\\nsource: x\\n---\\nThis is a sufficiently long prose sentence here.\\n'
    >>> significant_lines(doc)
    [(4, 'This is a sufficiently long prose sentence here.')]

    Fenced code and table rows are skipped, short lines dropped:

    >>> doc = 'short\\n```\\ncode line that is quite long but fenced away here\\n```\\n' \\
    ...       '| a table row that is long enough to exceed the length gate |\\n' \\
    ...       'A genuine prose line that is definitely long enough to count.\\n'
    >>> significant_lines(doc)
    [(6, 'A genuine prose line that is definitely long enough to count.')]

    A heading is never significant even when long:

    >>> significant_lines('## A heading that is quite long but still a heading here\\n')
    []
    """
    out = []
    lines = text.split("\n")
    in_fence = False
    fence_marker = ""
    # Guardrail #1: skip a leading YAML frontmatter block.
    start = 0
    if lines and lines[0].strip() == "---":
        for i in range(1, len(lines)):
            if lines[i].strip() == "---":
                start = i + 1
                break
    for idx in range(start, len(lines)):
        lineno = idx + 1
        line = lines[idx]
        stripped = line.strip()
        # Guardrail #2: fenced code blocks (``` or ~~~).
        if stripped.startswith("```") or stripped.startswith("~~~"):
            marker = "```" if stripped.startswith("```") else "~~~"
            if not in_fence:
                in_fence = True
                fence_marker = marker
            elif marker == fence_marker:
                in_fence = False
                fence_marker = ""
            continue
        if in_fence:
            continue
        if not stripped:
            continue
        if stripped.startswith("#"):
            continue
        # Guardrail #3: table rows (and, defensively, KQL pipe lines).
        if stripped.startswith("|"):
            continue
        if len(stripped) < min_length:
            continue
        out.append((lineno, stripped))
    return out


def load_line_set(path):
    """Load a set of non-comment, non-blank stripped lines from ``path``.

    Missing files yield an empty set (allowlist / markers are optional):

    >>> load_line_set('/nonexistent/path/xyz') == set()
    True
    """
    result = set()
    if not path or not os.path.exists(path):
        return result
    with open(path, encoding="utf-8") as fh:
        for raw in fh:
            s = raw.strip()
            if not s or s.startswith("#"):
                continue
            result.add(s)
    return result


def is_marker(line, markers):
    """True if ``line`` contains any marker substring (case-insensitive).

    >>> is_marker('Focus for landing standards and review model: ...', ['focus for'])
    True
    >>> is_marker('An ordinary sentence.', ['focus for'])
    False
    """
    low = line.lower()
    return any(m.lower() in low for m in markers)


def analyze_file(path, threshold, min_length, markers, allowlist):
    """Return ``(errors, warnings)`` for one file.

    Each element is ``(line_text, count, [linenos])``. ``errors`` are marker hits,
    ``warnings`` are generic repeats. Allowlisted lines are excluded from both.
    """
    with open(path, encoding="utf-8") as fh:
        text = fh.read()
    occurrences = defaultdict(list)
    for lineno, stripped in significant_lines(text, min_length=min_length):
        occurrences[stripped].append(lineno)
    errors, warnings = [], []
    for line, linenos in occurrences.items():
        if len(linenos) < threshold:
            continue
        if line in allowlist:
            continue
        entry = (line, len(linenos), linenos)
        if is_marker(line, markers):
            errors.append(entry)
        else:
            warnings.append(entry)
    errors.sort(key=lambda e: -e[1])
    warnings.sort(key=lambda e: -e[1])
    return errors, warnings


def iter_markdown_files(paths):
    """Yield ``.md`` files under the given files/directories, sorted."""
    files = []
    for p in paths:
        if os.path.isfile(p):
            if p.endswith(".md"):
                files.append(p)
        elif os.path.isdir(p):
            for root, _dirs, names in os.walk(p):
                for name in names:
                    if name.endswith(".md"):
                        files.append(os.path.join(root, name))
    return sorted(set(files))


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    parser.add_argument(
        "paths",
        nargs="*",
        default=["docs"],
        help="Files or directories to scan (default: docs).",
    )
    parser.add_argument(
        "--threshold",
        type=int,
        default=DEFAULT_THRESHOLD,
        help=f"Repeat count to flag (default: {DEFAULT_THRESHOLD}).",
    )
    parser.add_argument(
        "--min-length",
        type=int,
        default=DEFAULT_MIN_LENGTH,
        help=f"Minimum line length to consider (default: {DEFAULT_MIN_LENGTH}).",
    )
    parser.add_argument(
        "--markers-file",
        default=DEFAULT_MARKERS_FILE,
        help="File of boilerplate marker substrings (ERROR on repeat).",
    )
    parser.add_argument(
        "--allowlist",
        default=DEFAULT_ALLOWLIST_FILE,
        help="File of exact lines exempt from flagging.",
    )
    args = parser.parse_args(argv)

    paths = args.paths or ["docs"]
    markers = sorted(load_line_set(args.markers_file))
    allowlist = load_line_set(args.allowlist)
    files = iter_markdown_files(paths)

    total_errors = 0
    total_warnings = 0
    for path in files:
        errors, warnings = analyze_file(
            path, args.threshold, args.min_length, markers, allowlist
        )
        if not errors and not warnings:
            continue
        print(f"\n=== {path} ===")
        for line, count, linenos in errors:
            total_errors += 1
            loc = ", ".join(str(n) for n in linenos)
            print(
                f"  ::error:: {count}x (lines {loc}) marker boilerplate: {line[:110]}"
            )
        for line, count, linenos in warnings:
            total_warnings += 1
            loc = ", ".join(str(n) for n in linenos)
            print(f"  ::warning:: {count}x (lines {loc}) repeated prose: {line[:110]}")

    print(
        f"\nScanned {len(files)} file(s): "
        f"{total_errors} error(s), {total_warnings} warning(s)."
    )
    if total_errors:
        print(
            "ERROR: known boilerplate markers repeated. Remove the scaffold or, if "
            "genuinely legitimate, add the exact line to the allowlist."
        )
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
