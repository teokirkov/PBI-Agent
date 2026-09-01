#!/usr/bin/env python3
"""TMDL syntax-shape checker for the ToyCompanySales PBIP.

Companion to `validate_tmdl.py`, deliberately kept separate. That script checks
*cross-references* — does every name resolve against every other name — and its
own docstring is careful to say it "cannot tell you whether Power BI Desktop
accepts every keyword". This script is the other half: the specific syntax
shapes real Desktop has **already rejected on this project**.

Every check below is a Desktop error that actually happened, recorded in
`NOTES.md` §8. Before this file existed, each of those six fixes was verified by
an ad-hoc grep run once and then discarded, so nothing stopped a later run from
reintroducing the same shape in a new file — which is exactly what happened on
the seventh attempt, in `expressions.tmdl`, after the Databricks rewrite.

  check  Desktop error                                              attempt
  -----  ---------------------------------------------------------  -------
    1    InvalidLineType: Unexpected line type: Empty!                2, 4
         blank line between a /// block and the object it documents
    2    InvalidLineType: Unexpected line type: Other!                  3
         `//` at document level — legal only inside an M body
    3    Property 'description' is unknown and is not expected          5
         /// on `relationship`/`annotation`, which have no Description
    4    Cannot resolve all the paths while de-serializing Database     6
         `queryGroup:` / the `PBI_QueryGroups` annotation
    5    UnknownKeyword: The keyword 'let' is neither a property         7
         nor an object — content left after `=` on the declaration
         line of a value that then continues onto further lines

Run:  python3 projects/bi-task-1/validate_tmdl_syntax.py
      python3 projects/bi-task-1/validate_tmdl_syntax.py <definition-dir>

Exit status is 1 if anything fails, so it can gate a commit.

Note this is a shape checker, not a TMDL parser: it can only catch mistakes
this project has already made. A green run means "none of the seven known
failure modes", not "Desktop will open it".
"""

import pathlib
import re
import sys

DEFAULT = (pathlib.Path(__file__).resolve().parent
           / "ToyCompanySales.SemanticModel" / "definition")
MODEL = pathlib.Path(sys.argv[1]) if len(sys.argv) > 1 else DEFAULT

errors: list[str] = []


def fail(f: pathlib.Path, line: int, msg: str) -> None:
    entry = f"{f.name}:{line} {msg}"
    if entry not in errors:          # a multi-line /// block would report once per line
        errors.append(entry)


def doc_block_end(lines: list[str], i: int) -> int:
    """Index of the first line after the /// block starting at i."""
    j = i + 1
    while j < len(lines) and lines[j].strip().startswith("///"):
        j += 1
    return j


def indent_of(s: str) -> int:
    return len(s) - len(s.lstrip())


def inside_m_body(lines: list[str], i: int) -> bool:
    """True if line i sits inside a multi-line M value.

    `//` is valid M comment syntax and appears legitimately inside every
    partition `source = let … in …` block, so check 2 must not fire there.
    Walks outward to successively shallower indents; if the enclosing
    declaration is a `source =` or `expression X =`, we are in M.
    """
    indent = indent_of(lines[i])
    for j in range(i - 1, -1, -1):
        if not lines[j].strip():
            continue
        ind = indent_of(lines[j])
        if ind < indent:
            if re.match(r"^(source|expression\s+[\w']+)\s*=", lines[j].strip()):
                return True
            indent = ind
    return False


files = sorted(MODEL.rglob("*.tmdl"))
if not files:
    sys.exit(f"no .tmdl files under {MODEL}")

for f in files:
    lines = f.read_text(encoding="utf-8").split("\n")

    for i, line in enumerate(lines):
        s = line.strip()
        n = i + 1

        if s.startswith("///"):
            j = doc_block_end(lines, i)

            # 1. blank line between the /// block and its object
            if j < len(lines) and not lines[j].strip():
                k = j
                while k < len(lines) and not lines[k].strip():
                    k += 1
                if k < len(lines):   # trailing /// at EOF is not this bug
                    fail(f, j + 1, "blank line between a /// block and the object it "
                                   "documents (Desktop: InvalidLineType … Empty!)")

            # 3. /// on an object type with no Description property
            if j < len(lines):
                obj = lines[j].strip()
                if re.match(r"^(relationship|annotation)\b", obj):
                    fail(f, j + 1, f"/// attached to '{obj.split()[0]}', which has no "
                                   "Description property (Desktop: Property 'description' "
                                   "is unknown)")
            continue

        # 2. // at document level
        if s.startswith("//") and not inside_m_body(lines, i):
            fail(f, n, "'//' outside an M body — TMDL's only document-level comment "
                       "form is '///' (Desktop: InvalidLineType … Other!)")

        # 4. queryGroup / PBI_QueryGroups
        if re.match(r"^queryGroup\s*:", s) or "PBI_QueryGroups" in s:
            fail(f, n, "queryGroup/PBI_QueryGroups (Desktop: Cannot resolve all the "
                       "paths while de-serializing Database)")

        # 5. multi-line value with content left on the declaration line
        m = re.match(r"^(source|expression\s+[\w']+|measure\s+.+?|column\s+.+?)"
                     r"\s*=\s*(\S.*)$", s)
        if m:
            tail = m.group(2).rstrip()
            # an opener that cannot possibly complete the value on this line
            if tail.endswith(("=>", "let", "(", "&")):
                nxt = lines[i + 1] if i + 1 < len(lines) else ""
                if nxt.strip() and indent_of(nxt) > indent_of(line):
                    fail(f, n, "value continues onto the next line, so nothing may follow "
                               f"the '=' on the declaration line — {s[:60]}… "
                               "(Desktop: UnknownKeyword)")

print(f"scanned {len(files)} .tmdl files under {MODEL}")
if errors:
    for e in errors:
        print("  FAIL", e)
    print(f"\n{len(errors)} problem(s). See NOTES.md §8 for the Desktop error each maps to.")
    sys.exit(1)
print("clean: no blank-line-after-///, no document-level //, no /// on "
      "relationship/annotation,\n       no queryGroup/PBI_QueryGroups, no "
      "inline-then-continued multi-line value")
