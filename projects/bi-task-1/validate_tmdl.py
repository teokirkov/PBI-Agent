#!/usr/bin/env python3
"""Cross-reference checker for the ToyCompanySales PBIP.

Implements the "Validating your own output" checklist in
.claude/skills/pbip-tmdl-structure/SKILL.md, plus the equivalent checks for the
PBIR report layer. This checks *internal consistency* only — it is not a TMDL
parser and cannot tell you whether Power BI Desktop accepts every keyword.

Run:  python3 projects/bi-task-1/validate_tmdl.py
"""

import json
import pathlib
import re
import sys

ROOT = pathlib.Path(__file__).resolve().parent
MODEL = ROOT / "ToyCompanySales.SemanticModel" / "definition"
REPORT = ROOT / "ToyCompanySales.Report" / "definition"

errors: list[str] = []
notes: list[str] = []


def fail(msg: str) -> None:
    errors.append(msg)


# --------------------------------------------------------------- parse tables

def unquote(name: str) -> str:
    name = name.strip()
    if name.startswith("'") and name.endswith("'"):
        return name[1:-1]
    return name


def strip_comments(text: str) -> str:
    """Drop /// descriptions and // M comments so prose can't create matches."""
    out = []
    for line in text.splitlines():
        s = line.strip()
        if s.startswith("///") or s.startswith("//"):
            continue
        out.append(line)
    return "\n".join(out)


tables: dict[str, dict] = {}
for path in sorted((MODEL / "tables").glob("*.tmdl")):
    raw = path.read_text(encoding="utf-8")
    body = strip_comments(raw)

    decl = re.search(r"^table\s+(.+)$", body, re.M)
    if not decl:
        fail(f"{path.name}: no `table` declaration")
        continue
    tname = unquote(decl.group(1))

    if tname != path.stem:
        fail(f"{path.name}: declares `table '{tname}'` — filename must match the table name")

    cols: dict[str, dict] = {}
    for m in re.finditer(r"^\tcolumn\s+(.+)$", body, re.M):
        cname = unquote(m.group(1))
        block = body[m.end():]
        nxt = re.search(r"^\t(?:column|measure|partition|hierarchy|annotation)\s", block, re.M)
        block = block[: nxt.start()] if nxt else block
        dt = re.search(r"^\t\tdataType:\s*(\S+)", block, re.M)
        sort = re.search(r"^\t\tsortByColumn:\s*(.+)$", block, re.M)
        src = re.search(r"^\t\tsourceColumn:\s*(.+)$", block, re.M)
        cols[cname] = {
            "dataType": dt.group(1) if dt else None,
            "sortByColumn": unquote(sort.group(1)) if sort else None,
            "sourceColumn": (src.group(1).strip() if src else None),
            "inferred": "isNameInferred" in block,
        }

    measures = [unquote(m.group(1).split("=")[0]) for m in
                re.finditer(r"^\tmeasure\s+(.+)$", body, re.M)]

    parts = re.findall(r"^\tpartition\s+(.+?)\s*=\s*(\w+)\s*$", body, re.M)

    tables[tname] = {
        "path": path,
        "raw": raw,
        "body": body,
        "columns": cols,
        "measures": measures,
        "partitions": [(unquote(p[0]), p[1]) for p in parts],
        "hidden": re.search(r"^\tisHidden\s*$", body, re.M) is not None,
    }

all_measures = {m for t in tables.values() for m in t["measures"]}

# 1. Filenames <-> table names (checked above); partition name = table name
for tname, t in tables.items():
    for pname, _kind in t["partitions"]:
        if pname != tname:
            fail(f"{tname}: partition named '{pname}' does not match the table name")

# 2. model.tmdl ref-table list
model_text = (MODEL / "model.tmdl").read_text(encoding="utf-8")
refs = [unquote(m.group(1)) for m in re.finditer(r"^ref table\s+(.+)$", model_text, re.M)]
for r in refs:
    if r not in tables:
        fail(f"model.tmdl: `ref table '{r}'` has no matching tables/{r}.tmdl")
for tname in tables:
    if tname not in refs:
        fail(f"model.tmdl: table '{tname}' exists on disk but is not listed as `ref table`")

# PBI_QueryOrder should name real, M-backed queries or expressions
expr_text = (MODEL / "expressions.tmdl").read_text(encoding="utf-8")
expressions = re.findall(r"^expression\s+(\w+)", expr_text, re.M)
qo = re.search(r"PBI_QueryOrder = (\[.*\])", model_text)
if qo:
    for q in json.loads(qo.group(1)):
        if q not in tables and q not in expressions:
            fail(f"model.tmdl PBI_QueryOrder names '{q}', which is neither a table nor an expression")

# Date table must be marked as a date table
date_tbl = tables.get("Date")
if not date_tbl:
    fail("no 'Date' table")
else:
    if "dataCategory: Time" not in date_tbl["body"]:
        fail("Date: missing `dataCategory: Time`")
    if not re.search(r"^\t\tisKey\s*$", date_tbl["body"], re.M):
        fail("Date: no column marked `isKey`")
if "culture:" not in model_text:
    fail("model.tmdl: no culture set")

# 3. Relationships
rel_text = strip_comments((MODEL / "relationships.tmdl").read_text(encoding="utf-8"))
rels = re.findall(
    r"^relationship\s+(\S+)\n((?:\t.*\n?)+)", rel_text, re.M)
if not rels:
    fail("relationships.tmdl: no relationships parsed")

seen_rel_names = set()
for rname, blk in rels:
    if rname in seen_rel_names:
        fail(f"relationships.tmdl: duplicate relationship name '{rname}'")
    seen_rel_names.add(rname)

    ends = {}
    for side in ("fromColumn", "toColumn"):
        m = re.search(rf"^\t{side}:\s*(.+)$", blk, re.M)
        if not m:
            fail(f"{rname}: missing {side}")
            continue
        ref = m.group(1).strip()
        # 'Table'.Column  |  'Table'.'Column'  |  Table.Column
        pm = re.match(r"^('(?:[^']*)'|[^.]+)\.('(?:[^']*)'|.+)$", ref)
        if not pm:
            fail(f"{rname}: cannot parse {side} `{ref}`")
            continue
        tn, cn = unquote(pm.group(1)), unquote(pm.group(2))
        if tn not in tables:
            fail(f"{rname}: {side} references table '{tn}', which does not exist")
            continue
        if cn not in tables[tn]["columns"]:
            fail(f"{rname}: {side} references '{tn}'[{cn}], which does not exist")
            continue
        ends[side] = (tn, cn, tables[tn]["columns"][cn]["dataType"])

    if len(ends) == 2:
        (ft, fc, fdt), (tt, tc, tdt) = ends["fromColumn"], ends["toColumn"]
        if fdt != tdt:
            fail(f"{rname}: data type mismatch — '{ft}'[{fc}] is {fdt}, '{tt}'[{tc}] is {tdt}")
        if ft == tt:
            fail(f"{rname}: both ends are on '{ft}'")
    xf = re.search(r"^\tcrossFilteringBehavior:\s*(\S+)", blk, re.M)
    if xf and xf.group(1) not in ("oneDirection", "bothDirections", "automatic"):
        fail(f"{rname}: crossFilteringBehavior '{xf.group(1)}' is not a TOM enum value")

# 4. sortByColumn targets
for tname, t in tables.items():
    for cname, c in t["columns"].items():
        if c["sortByColumn"] and c["sortByColumn"] not in t["columns"]:
            fail(f"'{tname}'[{cname}]: sortByColumn '{c['sortByColumn']}' is not a column of that table")

# 5. DAX references across every measure and calculated partition
DAX_COLREF = re.compile(r"('(?:[^']*)'|(?<![\w'\[])[A-Za-z_]\w*)\[([^\]]+)\]")
DAX_TBLREF = re.compile(r"(?:COUNTROWS|ALL|ALLSELECTED|VALUES|DISTINCT|SUMMARIZE|FILTER)\s*\(\s*('(?:[^']*)'|[A-Za-z_]\w*)\s*\)")
BARE_MEASURE = re.compile(r"(?<![\w'\.\]])\[([^\]]+)\]")


def check_dax(where: str, dax: str, local_cols: set[str] | None = None) -> None:
    for m in DAX_COLREF.finditer(dax):
        tn, cn = unquote(m.group(1)), m.group(2)
        if tn not in tables:
            fail(f"{where}: DAX references table '{tn}', which does not exist")
            continue
        if cn not in tables[tn]["columns"]:
            fail(f"{where}: DAX references '{tn}'[{cn}], which does not exist")
    for m in DAX_TBLREF.finditer(dax):
        tn = unquote(m.group(1))
        if tn not in tables:
            fail(f"{where}: DAX references table '{tn}', which does not exist")
    # bare [Measure] references, minus qualified column refs and local ADDCOLUMNS names
    qualified = {m.group(0) for m in DAX_COLREF.finditer(dax)}
    for m in BARE_MEASURE.finditer(dax):
        if m.group(0) in qualified:
            continue
        name = m.group(1)
        if local_cols and name in local_cols:
            continue
        if name not in all_measures:
            fail(f"{where}: references measure [{name}], which is not defined")


for tname, t in tables.items():
    body = t["body"]
    for m in re.finditer(r"^\tmeasure\s+(.+?)\s*=", body, re.M):
        mname = unquote(m.group(1))
        block = body[m.end():]
        nxt = re.search(r"^\t(?:measure|column|partition)\s", block, re.M)
        block = block[: nxt.start()] if nxt else block
        dax = re.sub(r"^\t\t(?:formatString|displayFolder|isHidden|lineageTag|annotation).*$", "",
                     block, flags=re.M)
        check_dax(f"[{mname}]", dax)

    for pname, kind in t["partitions"]:
        if kind != "calculated":
            continue
        src = re.search(r"^\tpartition .*= calculated\n(?:\t\t.*\n)*", body, re.M)
        if not src:
            continue
        dax = src.group(0)
        # ADDCOLUMNS-created names are legal [Col] refs inside the same expression
        local = set(re.findall(r'"([^"]+)",', dax)) | set(t["columns"])
        check_dax(f"{tname} (calculated table)", dax, local_cols=local)

# 6. M expression references
for tname, t in tables.items():
    for pname, kind in t["partitions"]:
        if kind != "m":
            continue
        for name in re.findall(r"\b(stg\w+|SourceFolderPath)\b", t["body"]):
            if name not in expressions:
                fail(f"{tname}: M source references '{name}', which is not an expression")

for name in re.findall(r"\b(stg\w+|SourceFolderPath)\b", strip_comments(expr_text)):
    if name not in expressions:
        fail(f"expressions.tmdl: references '{name}', which is not defined")

# 7. sourceColumn present on every non-calculated column
for tname, t in tables.items():
    kinds = {k for _, k in t["partitions"]}
    for cname, c in t["columns"].items():
        if not c["sourceColumn"]:
            fail(f"'{tname}'[{cname}]: no sourceColumn")
            continue
        if "m" in kinds and c["inferred"]:
            fail(f"'{tname}'[{cname}]: isNameInferred on an M-backed table")
        if "calculated" in kinds and "m" not in kinds:
            if not c["sourceColumn"].startswith("["):
                fail(f"'{tname}'[{cname}]: calculated-table column sourceColumn should be [Name]")

# 8. No two tables claim the same relationship key name unintentionally
key_owners: dict[str, list[str]] = {}
for rname, blk in rels:
    for side in ("fromColumn", "toColumn"):
        m = re.search(rf"^\t{side}:\s*(.+)$", blk, re.M)
        if not m:
            continue
        pm = re.match(r"^('(?:[^']*)'|[^.]+)\.('(?:[^']*)'|.+)$", m.group(1).strip())
        if pm:
            key_owners.setdefault(unquote(pm.group(2)), []).append(unquote(pm.group(1)))
for k, owners in key_owners.items():
    if len(set(owners)) > 2:
        notes.append(f"key column name '{k}' is used by {len(set(owners))} tables: {sorted(set(owners))}")

# ------------------------------------------------------------ report (PBIR)

if REPORT.exists():
    pages_meta = json.loads((REPORT / "pages" / "pages.json").read_text(encoding="utf-8"))
    on_disk = {p.name for p in (REPORT / "pages").iterdir() if p.is_dir()}
    for p in pages_meta["pageOrder"]:
        if p not in on_disk:
            fail(f"pages.json lists page '{p}' with no folder")
    for p in on_disk:
        if p not in pages_meta["pageOrder"]:
            fail(f"page folder '{p}' is not in pages.json pageOrder")
    if pages_meta.get("activePageName") not in pages_meta["pageOrder"]:
        fail("pages.json activePageName is not one of the pages")

    visual_names: dict[str, str] = {}
    for vf in sorted((REPORT / "pages").rglob("visuals/*/visual.json")):
        page = vf.parents[2].name
        try:
            v = json.loads(vf.read_text(encoding="utf-8"))
        except json.JSONDecodeError as e:
            fail(f"{vf.relative_to(ROOT)}: invalid JSON — {e}")
            continue
        vname = v.get("name")
        if vname != vf.parent.name:
            fail(f"{vf.relative_to(ROOT)}: name '{vname}' != folder '{vf.parent.name}'")
        if vname in visual_names:
            fail(f"duplicate visual name '{vname}' ({visual_names[vname]} and {page})")
        visual_names[vname] = page

        blob = json.dumps(v)
        # every Entity/Property pair must resolve against the model
        for expr in re.finditer(
            r'\{"(?:Column|Measure|Aggregation|HierarchyLevel)":\s*\{.*?"Entity":\s*"([^"]+)".*?"Property":\s*"([^"]+)"',
                blob):
            tn, prop = expr.group(1), expr.group(2)
            if tn not in tables:
                fail(f"{page}/{vname}: binds to table '{tn}', which does not exist")
                continue
            if prop not in tables[tn]["columns"] and prop not in tables[tn]["measures"]:
                fail(f"{page}/{vname}: binds to '{tn}'[{prop}], which is neither a column nor a measure")
            if prop in tables[tn]["columns"] and tables[tn]["hidden"]:
                notes.append(f"{page}/{vname}: binds to hidden table '{tn}'")

    pbir = json.loads((ROOT / "ToyCompanySales.Report" / "definition.pbir").read_text(encoding="utf-8"))
    smpath = pbir["datasetReference"]["byPath"]["path"]
    if not (ROOT / "ToyCompanySales.Report" / smpath).resolve().exists():
        fail(f"definition.pbir points at '{smpath}', which does not exist")

# ------------------------------------------------------------------- summary

print(f"tables:        {len(tables)} ({', '.join(sorted(tables))})")
print(f"measures:      {len(all_measures)}")
print(f"relationships: {len(rels)}")
print(f"expressions:   {len(expressions)} ({', '.join(expressions)})")
if REPORT.exists():
    print(f"pages:         {len(pages_meta['pageOrder'])}")
    print(f"visuals:       {len(visual_names)}")
print()
for n in notes:
    print(f"note:  {n}")
if errors:
    for e in errors:
        print(f"ERROR: {e}")
    print(f"\n{len(errors)} error(s).")
    sys.exit(1)
print("All cross-references resolve.")
