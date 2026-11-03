"""Offline guard for the literal Functions v1 family, not a Mermaid parser.

Only the documented one-node/edge-per-line subset is accepted. Rendering and
source truth still require review; no generated output or Azure call is involved.
"""

import re
from pathlib import Path
from typing import Final

import pytest

PAGE: Final = Path(__file__).resolve().parents[1] / "docs/reference/functions-topology-templates.md"
BASE: Final = ("scale_controller", "client", "app_runtime", "language_worker", "storage_db")
VIEWS: Final = tuple(
    f"functions-v1-{kind}-{state}"
    for kind in ("base", "trigger", "network-storage")
    for state in ("normal", "failure")
)
SEQUENCE: Final = "functions-v1-worker-sequence"
FENCE: Final = re.compile(r"<!-- diagram-id: ([\w-]+) -->\n```mermaid\n(.*?)\n```", re.DOTALL)
NODE: Final = re.compile(r'^\s*(\w+)(\[\[|\[\(|\(\[|\{\{|\[|>)("[^"]+")(\]\]|\)\]|\]\)|\}\}|\])$')
EDGE: Final = re.compile(r'^\s*(\w+) (-->|-\.->|==>|~~~)(?:\|"([^"\n]+)"\|)? (\w+)$')
CONTAINER: Final = re.compile(r'^\s*subgraph (\w+)\["([^"]+)"\]$')
STYLE: Final = re.compile(r"^\s*linkStyle (\d+(?:,\d+)*) (.+);$")
CLAIM: Final = re.compile(r"^\[(?:Configured|Illustrative|Inferred)\] ")
SHAPES: Final = {
    "client": ("([", "])"), "storage_db": ("[(", ")]"),
    "app_runtime": ("[", "]"), "language_worker": ("[", "]"),
    "scale_controller": ("[", "]"), "trigger_listener": ("[", "]"),
    "dns_fn": ("{{", "}}"), "vnet_integration": ("[[", "]]"),
    "pe_storage": ("[[", "]]"),
}


def topology_problems(code: str) -> list[str]:
    """Check references, restricted syntax, edge claims, and factual containers."""
    problems: list[str] = []
    nodes: list[str] = []
    containers: list[str] = []
    placement: dict[str, tuple[str, ...]] = {}
    edges: list[tuple[str, str, str, str]] = []
    styles: dict[int, str] = {}
    for line in code.splitlines()[3:]:
        if match := CONTAINER.fullmatch(line):
            name, title = match.groups()
            if re.search(r"/\d{1,3}\b", title):
                problems.append("CIDR in container title")
            if name.startswith("subnet_") and (not containers or not containers[-1].startswith("vnet_")):
                problems.append("subnet outside VNet")
            containers.append(name)
        elif line.strip() == "end":
            if containers:
                containers.pop()
            else:
                problems.append("unbalanced container")
        elif match := NODE.fullmatch(line):
            name, opening, label, closing = match.groups()
            nodes.append(name)
            placement[name] = tuple(containers)
            if SHAPES.get(name) != (opening, closing):
                problems.append("unknown component or wrong shape")
            if name in ("app_runtime", "language_worker") and containers:
                problems.append("runtime inside customer container")
            if (name.startswith("dns") or "Private DNS zone" in label) and containers:
                problems.append("DNS inside customer container")
        elif match := EDGE.fullmatch(line):
            source, arrow, label, target = match.groups()
            edges.append((source, arrow, label or "", target))
            if arrow != "~~~" and not (CLAIM.match(label or "") or (arrow == "==>" and (label or "").startswith("[FAULT / Illustrative] "))):
                problems.append("missing edge claim or fault prefix")
            if arrow == "~~~" and label:
                problems.append("label on layout anchor")
            if target.startswith("dns") and arrow != "-.->":
                problems.append("DNS lookup must be dotted")
            if source.startswith("dns"):
                problems.append("DNS lookup starts at zone")
        elif match := STYLE.fullmatch(line):
            styles.update((int(index), match[2]) for index in match[1].split(","))
        elif not re.fullmatch(r"\s*(?:classDef .+;|class .+;|linkStyle default stroke-width:2px;|%%.*|)", line):
            problems.append("unsupported topology line")
    if containers:
        problems.append("unbalanced container")
    if len(nodes) != len(set(nodes)):
        problems.append("duplicate node")
    if tuple(n for n in nodes if n in BASE) != BASE:
        problems.append("base IDs or declaration order differ")
    for source, _, _, target in edges:
        if source not in nodes or target not in nodes:
            problems.append("undeclared edge endpoint")
    if any(index >= len(edges) for index in styles):
        problems.append("linkStyle index out of range")
    faults = {i for i, (_, arrow, _, _) in enumerate(edges) if arrow == "==>"}
    if set(styles) != faults or any("stroke:#da495d,stroke-width:3px" not in styles[i] for i in faults & styles.keys()):
        problems.append("fault linkStyle differs from fault edges")
    for name in ("vnet_integration", "pe_storage"):
        if name in nodes:
            chain = placement[name]
            expected = "subnet_int_fn" if name == "vnet_integration" else "subnet_pe_fn"
            if chain != ("vnet_fn", expected):
                problems.append("NIC outside its dedicated subnet")
    return problems


def template_problems(text: str) -> list[str]:
    """Check the complete registered family; return deterministic diagnostics."""
    problems: list[str] = []
    frontmatter = text.split("---", 2)[1] if text.startswith("---\n") else ""
    declared = re.findall(r"^    - id: ([\w-]+)$", frontmatter, re.MULTILINE)
    fixtures = FENCE.findall(text)
    ids = [name for name, _ in fixtures]
    if len(fixtures) != text.count("```mermaid") or sorted(ids) != sorted(declared) or len(set(ids)) != len(ids):
        problems.append("diagram-id and metadata mismatch")
    if set(ids) != {*VIEWS, SEQUENCE}:
        problems.append("missing or unexpected variant")
    base_declarations: list[tuple[str, ...]] = []
    for name, code in fixtures:
        for keyword in ("accTitle", "accDescr"):
            if not re.search(rf"^    {keyword}: [^\s\n].*$", code, re.MULTILINE):
                problems.append(f"missing or empty {keyword}")
        if "[Observed]" in code or "/ Observed]" in code:
            # This synthetic family has no retained lab artifact: fail closed.
            problems.append("Observed without retained artifact")
        if "<-->" in code:
            problems.append("bidirectional topology edge")
        if name in VIEWS:
            if not code.startswith("flowchart TD\n"):
                problems.append("topology orientation/type")
            problems.extend(topology_problems(code))
            base_declarations.append(tuple(line.strip() for line in code.splitlines() if (m := NODE.fullmatch(line)) and m[1] in BASE))
            if name.endswith("failure") and "==>" not in code:
                problems.append("failure lacks anchored fault")
        elif name == SEQUENCE:
            if not code.startswith("sequenceDiagram\n"):
                problems.append("sequence type")
            participants = re.findall(r"^    participant (\w+) as .+$", code, re.MULTILINE)
            for source, target in re.findall(r"^    (\w+)-{1,2}>>(\w+):", code, re.MULTILINE):
                if source not in participants or target not in participants:
                    problems.append("undeclared sequence endpoint")
    if base_declarations and any(declarations != base_declarations[0] for declarations in base_declarations):
        problems.append("base declarations differ across variants")
    return problems


def test_committed_templates() -> None:
    # Given: the literal source actually consumed by MkDocs.
    text = PAGE.read_text(encoding="utf-8")
    # When: the offline guard checks all views twice (no mutable parser state).
    results = (template_problems(text), template_problems(text))
    # Then: both checks accept the complete family deterministically.
    assert results == ([], [])


@pytest.mark.parametrize(("old", "new", "diagnostic"), [
    ('| client', '| ghost', "undeclared edge endpoint"),
    ('scale_controller["', 'renamed_controller["', "base IDs or declaration order differ"),
    ('    client([', '    language_worker["Extra"]\n    client([', "base IDs or declaration order differ"),
    ('linkStyle 4 ', 'linkStyle 999 ', "linkStyle index out of range"),
    ('accTitle:', 'accTit:', "missing or empty accTitle"),
    ('accDescr:', 'accDesc:', "missing or empty accDescr"),
    ('accTitle: Functions base - host coordination', 'accTitle: ', "missing or empty accTitle"),
    ('accDescr: Premium queue polling and isolated-worker invocation are separate from scaling metadata and Blob host storage. All boxes are logical roles, not subnet placement.', 'accDescr: ', "missing or empty accDescr"),
    ('    - id: functions-v1-base-normal', '    - id: wrong-id', "diagram-id and metadata mismatch"),
    ('<!-- diagram-id: functions-v1-base-normal -->', '<!-- missing-id -->', "diagram-id and metadata mismatch"),
    ('app_runtime -->', 'app_runtime <-->', "bidirectional topology edge"),
    ('Customer VNet &nbsp;', 'Customer VNet /27 &nbsp;', "CIDR in container title"),
    ('[Configured]', '[Observed]', "Observed without retained artifact"),
    ('    app_runtime["', '    subgraph subnet_bad["Subnet: bad"]\n    app_runtime["', "runtime inside customer container"),
    ('    dns_fn{{', '    subgraph vnet_bad["Customer VNet"]\n    dns_fn{{', "DNS inside customer container"),
    ('    pe_storage[[', '    pe_storage[', "unknown component or wrong shape"),
    ('subgraph subnet_pe_fn[', 'subgraph subnet_int_fn[', "NIC outside its dedicated subnet"),
    ('[Configured] Monitor event rate', 'Monitor event rate', "missing edge claim or fault prefix"),
    ('==>|"[FAULT / Illustrative]', '-->|"[FAULT / Illustrative]', "missing edge claim or fault prefix"),
    ('linkStyle 4 stroke:#da495d,stroke-width:3px', 'linkStyle 4 stroke:#ffffff,stroke-width:0px', "fault linkStyle differs from fault edges"),
    ('flowchart TD', 'flowchart LR', "topology orientation/type"),
    ('\nsequenceDiagram\n', '\nflowchart TD\n', "sequence type"),
    ('app_runtime->>language_worker:', 'app_runtime->>ghost:', "undeclared sequence endpoint"),
    (' -->|"[Configured] Poll queue"| client', ' ~~~|"[Configured] Poll queue"| client', "label on layout anchor"),
    (' -.->|"[Configured] DNS returns PE IP"| dns_fn', ' -->|"[Configured] DNS returns PE IP"| dns_fn', "DNS lookup must be dotted"),
    ('    class client,language_worker,storage_db baseNeutral;', '    garbage', "unsupported topology line"),
    ('[Public endpoint]', '[Other endpoint]', "base declarations differ across variants"),
    ('    client([', '    client(["Duplicate"])\n    client([', "duplicate node"),
    ('subgraph vnet_fn[', 'subgraph subnet_bad[', "subnet outside VNet"),
    ('    end\n    scale_controller -.->', '    scale_controller -.->', "unbalanced container"),
    ('    app_runtime -.->|"[Configured] DNS returns PE IP"| dns_fn', '    dns_fn -.->|"[Configured] DNS returns PE IP"| app_runtime', "DNS lookup starts at zone"),
    ('    app_runtime ==>|"[FAULT / Illustrative] Storage unavailable"| storage_db', '', "failure lacks anchored fault"),
])
def test_rejects_mutated_templates(old: str, new: str, diagnostic: str) -> None:
    # Given: a single in-memory defect in the committed page.
    text = PAGE.read_text(encoding="utf-8")
    assert old in text, "mutation must still exercise its target"
    mutated = text.replace(old, new, 1)
    # When: the same guard used for the real page processes the defect.
    problems = template_problems(mutated)
    # Then: its specific rule fires, not merely an incidental parser failure.
    assert diagnostic in problems
