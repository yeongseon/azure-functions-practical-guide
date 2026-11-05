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
STYLE: Final = re.compile(r"^\s*linkStyle (\d+(?:,\d+)*) ([^;]+);$")
CLAIM: Final = re.compile(r"\[(?:Configured|Illustrative|Inferred|Observed)\] \S.*")
FAULT: Final = re.compile(r"\[FAULT / (?:Illustrative|Inferred|Observed)\] \S.*")
PALETTE: Final = {
    "baseNeutral": "fill:#f2f4f8,stroke:#707e93,stroke-width:1.5px,color:#14202e",
    "focusActive": "fill:#e6f0fd,stroke:#287ce4,stroke-width:2.5px,color:#14202e",
    "bandMuted": "fill:#ffffff,stroke:#707e93,stroke-width:1.5px,stroke-dasharray:4 3,color:#14202e",
    "stateFault": "fill:#fdebee,stroke:#da495d,stroke-width:3px,color:#86172a",
    "netBox": "fill:transparent,stroke:#287ce4,stroke-width:2px,stroke-dasharray:6 3",
}
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
    container_ids: list[str] = []
    classes: set[str] = set()
    assignments: list[tuple[str, str]] = []
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
            container_ids.append(name)
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
            if containers and name not in ("vnet_integration", "pe_storage"):
                problems.append("service inside customer container")
        elif match := EDGE.fullmatch(line):
            source, arrow, label, target = match.groups()
            if containers:
                problems.append("edge inside customer container")
            edges.append((source, arrow, label or "", target))
            if arrow != "~~~" and not (FAULT if arrow == "==>" else CLAIM).fullmatch(label or ""):
                problems.append("missing edge claim or fault prefix")
            if arrow == "~~~" and label:
                problems.append("label on layout anchor")
            if target.startswith("dns") and arrow not in ("-.->", "~~~"):
                problems.append("DNS lookup must be dotted")
            if source.startswith("dns") and arrow != "~~~":
                problems.append("DNS lookup starts at zone")
        elif match := STYLE.fullmatch(line):
            styles.update((int(index), match[2]) for index in match[1].split(","))
        elif match := re.fullmatch(r"\s*classDef (\w+) ([^;]+);", line):
            classes.add(match[1])
            if PALETTE.get(match[1]) != match[2]:
                problems.append("unsupported class palette")
        elif match := re.fullmatch(r"\s*class (\w+(?:,\w+)*) (\w+);", line):
            assignments.extend((member, match[2]) for member in match[1].split(","))
        elif not re.fullmatch(r"\s*(?:linkStyle default stroke-width:2px;|%%.*|)", line):
            problems.append("unsupported topology line")
    if containers:
        problems.append("unbalanced container")
    if len(nodes) != len(set(nodes)):
        problems.append("duplicate node")
    if len(container_ids) != len(set(container_ids)) or set(container_ids) & set(nodes):
        problems.append("duplicate container")
    if set(nodes + container_ids) - {member for member, _ in assignments}:
        problems.append("missing class assignment")
    for member, class_name in assignments:
        if member not in nodes + container_ids:
            problems.append("undeclared class member")
        if class_name not in classes:
            problems.append("undefined class")
    if tuple(n for n in nodes if n in BASE) != BASE:
        problems.append("base IDs or declaration order differ")
    for source, _, _, target in edges:
        if source not in nodes or target not in nodes:
            problems.append("undeclared edge endpoint")
    if any(index >= len(edges) for index in styles):
        problems.append("linkStyle index out of range")
    faults = {i for i, (_, arrow, _, _) in enumerate(edges) if arrow == "==>"}
    if set(styles) != faults or any(styles[i] != "stroke:#da495d,stroke-width:3px" for i in faults & styles.keys()):
        problems.append("fault linkStyle differs from fault edges")
    for name in ("vnet_integration", "pe_storage"):
        if name in nodes:
            chain = placement[name]
            expected = "subnet_int_fn" if name == "vnet_integration" else "subnet_pe_fn"
            if chain != ("vnet_fn", expected):
                problems.append("NIC outside its dedicated subnet")
    return problems


def sequence_problems(code: str) -> list[str]:
    """Accept only the declared host/worker pair and one ordered exchange."""
    problems: list[str] = []
    participants: list[str] = []
    messages: list[tuple[str, str, str]] = []
    for line in code.splitlines()[3:]:
        if ";" in line:
            problems.append("sequence requires one statement per line")
        elif "%%" in line or "\t" in line:
            problems.append("unsupported sequence comment or tab")
        elif match := re.fullmatch(r"    participant ([a-z_]+) as \S.*", line):
            participants.append(match[1])
            if messages:
                problems.append("participant after sequence message")
        elif match := re.fullmatch(r"    ([a-z_]+)(->>|-->>)([a-z_]+): (.*)", line):
            source, arrow, target, label = match.groups()
            messages.append((source, arrow, target))
            if source not in participants or target not in participants:
                problems.append("undeclared sequence endpoint")
            if not CLAIM.fullmatch(label):
                problems.append("missing sequence claim or description")
        else:
            problems.append("unsupported sequence statement")
    if len(participants) != len(set(participants)):
        problems.append("duplicate participant")
    if participants != ["app_runtime", "language_worker"]:
        problems.append("sequence participant IDs or declaration order differ")
    expected = [("app_runtime", "->>", "language_worker"), ("language_worker", "-->>", "app_runtime")]
    for purpose, relationship in zip(("invocation", "completion"), expected, strict=True):
        count = messages.count(relationship)
        if count == 0:
            problems.append(f"essential sequence relationship: {purpose}")
        elif count > 1:
            problems.append(f"duplicate sequence relationship: {purpose}")
    if any(message not in expected for message in messages):
        problems.append("unexpected sequence relationship")
    if len(messages) == 2 and set(messages) == set(expected) and messages != expected:
        problems.append("sequence exchange order differs")
    return problems


def relationship_problems(name: str, code: str) -> list[str]:
    edges = {(m[1], m[2], m[4]) for line in code.splitlines() if (m := EDGE.fullmatch(line))}
    failure = name.endswith("failure")
    trigger = "-trigger-" in name
    network = "-network-storage-" in name
    expected = [
        ("poll", "trigger_listener" if trigger else "app_runtime", "==>" if trigger and failure else "-->", "client"),
        ("invoke", "app_runtime", "-->", "language_worker"),
        ("scale", "scale_controller", "-.->", "app_runtime"),
    ]
    if network:
        expected.extend([
            ("DNS", "app_runtime", "-.->", "dns_fn"),
            ("host storage", "app_runtime", "-->", "vnet_integration"),
            ("integration to PE", "vnet_integration", "==>" if failure else "-->", "pe_storage"),
            ("PE to storage", "pe_storage", "-->", "storage_db"),
        ])
    else:
        expected.append(("host storage", "app_runtime", "==>" if failure and not trigger else "-->", "storage_db"))
    return [f"essential relationship: {purpose}" for purpose, source, arrow, target in expected if (source, arrow, target) not in edges]


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
        lines = code.splitlines()
        for position, keyword in enumerate(("accTitle", "accDescr"), 1):
            if len(lines) <= position or not re.fullmatch(rf"    {keyword}: \S.*", lines[position]):
                problems.append(f"missing or empty {keyword}")
            elif any(token in lines[position] for token in ((";", "%%", "\t") if name == SEQUENCE else ("%%", "\t"))):
                problems.append("unsupported accessible header separator")
        if "[Observed]" in code or "/ Observed]" in code:
            # This synthetic family has no retained lab artifact: fail closed.
            problems.append("Observed without retained artifact")
        if "<-->" in code:
            problems.append("bidirectional topology edge")
        if name in VIEWS:
            if not code.startswith("flowchart TD\n"):
                problems.append("topology orientation/type")
            problems.extend(topology_problems(code))
            problems.extend(relationship_problems(name, code))
            base_declarations.append(tuple(line.strip() for line in code.splitlines() if (m := NODE.fullmatch(line)) and m[1] in BASE))
            if name.endswith("failure") and "==>" not in code:
                problems.append("failure lacks anchored fault")
        elif name == SEQUENCE:
            if not code.startswith("sequenceDiagram\n"):
                problems.append("sequence type")
            problems.extend(sequence_problems(code))
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
    ('    app_runtime["Compute: Functions host<br/>[Premium runtime]"]', '    subgraph vnet_bad["Customer VNet"]\n    app_runtime["Compute: Functions host<br/>[Premium runtime]"]\n    end', "runtime inside customer container"),
    ('    dns_fn{{"Private DNS zone: Blob<br/>[Linked to VNet]"}}', '    subgraph vnet_bad["Customer VNet"]\n    dns_fn{{"Private DNS zone: Blob<br/>[Linked to VNet]"}}\n    end', "DNS inside customer container"),
    ('pe_storage[["Private Endpoint: Storage NIC<br/>[Inbound private IP]"]]', 'pe_storage["Private Endpoint: Storage NIC<br/>[Inbound private IP]"]', "unknown component or wrong shape"),
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
    ('[FAULT / Illustrative] Storage unavailable', '[Configured] Storage unavailable', "missing edge claim or fault prefix"),
    ('[Configured] Poll queue', '[Configured] ', "missing edge claim or fault prefix"),
    ('app_runtime->>language_worker:', 'app_runtime->ghost:', "unsupported sequence statement"),
    ('app_runtime->>language_worker:', 'ghost->>language_worker:', "undeclared sequence endpoint"),
    ('[Illustrative] Invoke function', '[Illustrative] ', "missing sequence claim or description"),
    ('    participant language_worker as Isolated worker', '    participant language_worker as Isolated worker\n    participant language_worker as Duplicate', "duplicate participant"),
    ('    app_runtime->>language_worker:', '    garbage\n    app_runtime->>language_worker:', "unsupported sequence statement"),
    ('class client,language_worker,storage_db baseNeutral;', 'class client,language_worker,storage_db baseNeutral; app_runtime --> ghost;', "unsupported topology line"),
    ('class client,language_worker,storage_db baseNeutral;', 'class client,language_worker,ghost baseNeutral;', "undeclared class member"),
    ('class app_runtime focusActive;', 'class app_runtime mystery;', "undefined class"),
    ('classDef baseNeutral fill:#f2f4f8', 'classDef baseNeutral fill:#ffffff', "unsupported class palette"),
    ('linkStyle 4 stroke:#da495d,stroke-width:3px;', 'linkStyle 4 stroke:#da495d,stroke-width:3px,stroke:#ffffff,stroke-width:0px;', "fault linkStyle differs from fault edges"),
    ('classDef baseNeutral fill:#f2f4f8,', 'classDef baseNeutral fill:#f2f4f8,fill:#ffffff,', "unsupported class palette"),
    ('    class app_runtime focusActive;', '    style app_runtime fill:#ffffff;\n    class app_runtime focusActive;', "unsupported topology line"),
    ('    scale_controller -.->|"[Configured] Monitor event rate"| client', '    subgraph vnet_empty["Customer VNet"]\n    end\n    subgraph vnet_empty["Customer VNet"]\n    end\n    scale_controller -.->|"[Configured] Monitor event rate"| client', "duplicate container"),
    ('flowchart TD\n    accTitle:', 'garbage\n    accTitle:', "topology orientation/type"),
    ('flowchart TD\n    accTitle:', 'flowchart TD\n    garbage\n    accTitle:', "missing or empty accTitle"),
    ('    app_runtime -->|"[Configured] Poll queue"| client', '', "essential relationship: poll"),
    ('    app_runtime -->|"[Configured] Poll queue"| client', '    app_runtime ~~~ client', "essential relationship: poll"),
    ('    app_runtime -->|"[Configured] Poll queue"| client', '    app_runtime -.->|"[Configured] Poll queue"| client', "essential relationship: poll"),
    ('    app_runtime -->|"[Configured] Invoke function"| language_worker', '    app_runtime -.->|"[Configured] Invoke function"| language_worker', "essential relationship: invoke"),
    ('    scale_controller -.->|"[Configured] Adjust instances"| app_runtime', '', "essential relationship: scale"),
    ('    app_runtime -->|"[Configured] Host state / keys"| storage_db', '', "essential relationship: host storage"),
    ('    vnet_integration -->|"[Configured] Connect to PE IP"| pe_storage', '', "essential relationship: integration to PE"),
    ('    pe_storage -->|"[Configured] Private Link to Blob"| storage_db', '', "essential relationship: PE to storage"),
    ('[Illustrative] Invoke function', '[Illustrative] Invoke function; app_runtime->>ghost: [Illustrative] Extra', "sequence requires one statement per line"),
    ('as Functions host', 'as Functions host; participant ghost as Extra', "sequence requires one statement per line"),
    ('    app_runtime->>language_worker: [Illustrative] Invoke function\n', '', "essential sequence relationship: invocation"),
    ('\n    language_worker-->>app_runtime: [Illustrative] Complete invocation', '', "essential sequence relationship: completion"),
    ('\n    app_runtime->>language_worker: [Illustrative] Invoke function\n    language_worker-->>app_runtime: [Illustrative] Complete invocation', '', "essential sequence relationship: invocation"),
    ('\n    app_runtime->>language_worker: [Illustrative] Invoke function\n    language_worker-->>app_runtime: [Illustrative] Complete invocation', '', "essential sequence relationship: completion"),
    ('app_runtime->>language_worker:', 'language_worker->>app_runtime:', "essential sequence relationship: invocation"),
    ('language_worker-->>app_runtime:', 'app_runtime-->>language_worker:', "essential sequence relationship: completion"),
    ('app_runtime->>language_worker:', 'app_runtime-->>language_worker:', "essential sequence relationship: invocation"),
    ('language_worker-->>app_runtime:', 'language_worker->>app_runtime:', "essential sequence relationship: completion"),
    ('[Illustrative] Invoke function', '[Illustrative] Invoke function %% hidden', "unsupported sequence comment or tab"),
    ('[Illustrative] Invoke function', '[Illustrative] Invoke\tfunction', "unsupported sequence comment or tab"),
    ('as Functions host', 'as Functions host %% hidden', "unsupported sequence comment or tab"),
    ('as Functions host', 'as Functions\thost', "unsupported sequence comment or tab"),
    ('    participant app_runtime as Functions host', '    participant аpp_runtime as Functions host', "sequence participant IDs or declaration order differ"),
    ('    app_runtime->>language_worker:', '    аpp_runtime->>language_worker:', "unsupported sequence statement"),
    ('    app_runtime->>language_worker:', '    participant ghost as Extra\n    app_runtime->>language_worker:', "sequence participant IDs or declaration order differ"),
    ('    app_runtime->>language_worker: [Illustrative] Invoke function', '    app_runtime->>language_worker: [Illustrative] Invoke function\n    app_runtime->>language_worker: [Illustrative] Invoke function', "duplicate sequence relationship: invocation"),
    ('    language_worker-->>app_runtime: [Illustrative] Complete invocation', '    language_worker-->>app_runtime: [Illustrative] Complete invocation\n    language_worker-->>app_runtime: [Illustrative] Complete invocation', "duplicate sequence relationship: completion"),
    ('[Illustrative] Complete invocation', '[Illustrative] Complete invocation\n    language_worker->>app_runtime: [Illustrative] Extra', "unexpected sequence relationship"),
    ('    app_runtime->>language_worker: [Illustrative] Invoke function\n    language_worker-->>app_runtime: [Illustrative] Complete invocation', '    language_worker-->>app_runtime: [Illustrative] Complete invocation\n    app_runtime->>language_worker: [Illustrative] Invoke function', "sequence exchange order differs"),
    ('    participant language_worker as Isolated worker\n    app_runtime->>language_worker: [Illustrative] Invoke function', '    app_runtime->>language_worker: [Illustrative] Invoke function\n    participant language_worker as Isolated worker', "participant after sequence message"),
    ('    accTitle: Isolated worker - logical invocation exchange', '    accTitle: Isolated worker - logical invocation exchange; participant ghost as Extra', "unsupported accessible header separator"),
    ('accDescr: Premium queue polling', 'accDescr: Premium %% queue polling', "unsupported accessible header separator"),
    ('accDescr: Premium queue polling', 'accDescr: Premium\tqueue polling', "unsupported accessible header separator"),
    ('    app_runtime->>language_worker:', '\tapp_runtime->>language_worker:', "unsupported sequence comment or tab"),
    ('linkStyle 4 stroke:#da495d,stroke-width:3px;', 'linkStyle 4 stroke:#da495d,stroke-width:3px; app_runtime --> ghost;\n    linkStyle 4 stroke:#da495d,stroke-width:3px;', "unsupported topology line"),
    *[(
        '    app_runtime->>language_worker:',
        '    ' + statement + '\n    app_runtime->>language_worker:',
        "unsupported sequence statement",
    ) for statement in (
        'Note over app_runtime: Extra', 'activate app_runtime\n    deactivate app_runtime',
        'loop Extra\n    end', 'alt Extra\n    else Other\n    end',
        'autonumber', 'autonumber\n    autonumber', 'sequenceDiagram',
    )],
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


@pytest.mark.parametrize("prefix", [
    'scale_controller[', 'app_runtime -->', 'subgraph vnet_fn[', 'end',
    'linkStyle 6 ', 'classDef baseNeutral ', 'class ',
])
@pytest.mark.parametrize("separator", ["; ", " "])
def test_rejects_second_topology_statement(prefix: str, separator: str) -> None:
    # Given: a complete view, with balanced containers and an extra statement.
    text = PAGE.read_text(encoding="utf-8")
    code = dict(FENCE.findall(text))["functions-v1-network-storage-failure"]
    line = next(line for line in code.splitlines() if line.strip().startswith(prefix))
    mutated = code.replace(line, line + separator + 'app_runtime --> ghost;', 1)
    # When: the same family guard inspects the otherwise unchanged page.
    problems = template_problems(text.replace(code, mutated))
    # Then: statement recognition rejects the appended command itself.
    assert "unsupported topology line" in problems


def test_rejects_empty_sequence_body() -> None:
    # Given: valid headers but no participants or messages.
    text = PAGE.read_text(encoding="utf-8")
    code = dict(FENCE.findall(text))[SEQUENCE]
    mutated = text.replace(code, '\n'.join(code.splitlines()[:3]))
    # When: the family guard inspects the empty sequence.
    problems = template_problems(mutated)
    # Then: an invocation exchange is mandatory.
    assert "essential sequence relationship: invocation" in problems
    assert "essential sequence relationship: completion" in problems


def test_accepts_sequence_description_with_trailing_spaces() -> None:
    # Given: a claim-prefixed description, not an exact prose fixture.
    text = PAGE.read_text(encoding="utf-8")
    mutated = text.replace('[Illustrative] Invoke function', '[Configured] Dispatch work   ', 1)
    # When: the same bounded family guard inspects ordinary trailing whitespace.
    problems = template_problems(mutated)
    # Then: description wording and trailing spaces do not alter the exchange.
    assert problems == []


@pytest.mark.parametrize("member", [
    "all", *BASE, "dns_fn", "vnet_integration", "pe_storage",
    "vnet_fn", "subnet_int_fn", "subnet_pe_fn",
])
def test_rejects_missing_class_assignment(member: str) -> None:
    # Given: remove all assignments or only one declared component's membership.
    text = PAGE.read_text(encoding="utf-8")
    code = dict(FENCE.findall(text))["functions-v1-network-storage-normal"]
    lines: list[str] = []
    for line in code.splitlines():
        if match := re.fullmatch(r"\s*class (\w+(?:,\w+)*) (\w+);", line):
            members = [name for name in match[1].split(",") if member != "all" and name != member]
            if members:
                lines.append(f"    class {','.join(members)} {match[2]};")
        else:
            lines.append(line)
    mutated = "\n".join(lines)
    assert mutated != code, "mutation must still exercise its target"
    # When: the family guard processes retained class definitions without coverage.
    problems = template_problems(text.replace(code, mutated, 1))
    # Then: missing node or container styling is rejected, not a syntax defect.
    assert "missing class assignment" in problems
    assert "unsupported topology line" not in problems


@pytest.mark.parametrize("edge_prefix", [
    '    app_runtime -->|"[Configured] Invoke function"|',
    '    client ~~~',
])
def test_rejects_edge_inside_balanced_vnet(edge_prefix: str) -> None:
    # Given: move an existing edge just inside the balanced customer VNet.
    text = PAGE.read_text(encoding="utf-8")
    code = dict(FENCE.findall(text))["functions-v1-network-storage-normal"]
    edge = next(line for line in code.splitlines() if line.startswith(edge_prefix))
    moved = code.replace(edge + "\n", "", 1).replace(
        '    end\n    scale_controller -.->',
        edge + '\n    end\n    scale_controller -.->',
        1,
    )
    assert moved != code, "mutation must still exercise its target"
    # When: the family guard processes implicit endpoint containment.
    problems = template_problems(text.replace(code, moved, 1))
    # Then: neither semantic edges nor layout anchors may imply membership.
    assert "edge inside customer container" in problems
    assert "unbalanced container" not in problems


def test_rejects_storage_service_inside_balanced_subnet() -> None:
    # Given: move only Storage into the existing, balanced PE subnet.
    text = PAGE.read_text(encoding="utf-8")
    code = next(code for name, code in FENCE.findall(text) if name == "functions-v1-network-storage-normal")
    declaration = next(line for line in code.splitlines() if line.strip().startswith('storage_db[('))
    moved = code.replace(declaration + "\n", "").replace('            pe_storage[[', declaration + '\n            pe_storage[[')
    # When: the same topology guard inspects factual containment.
    problems = topology_problems(moved)
    # Then: it rejects the service, not an unbalanced container.
    assert "service inside customer container" in problems
    assert "unbalanced container" not in problems


def test_accepts_unlabeled_dns_layout_anchor() -> None:
    # Given: an extra invisible anchor, not a DNS query.
    code = next(code for name, code in FENCE.findall(PAGE.read_text(encoding="utf-8")) if name == "functions-v1-network-storage-normal")
    # When: the complete otherwise-valid normal view is checked.
    problems = topology_problems(code + "\n    app_runtime ~~~ dns_fn")
    # Then: purpose-specific arrow rules do not apply to layout anchors.
    assert problems == []


@pytest.mark.parametrize(("kind", "expected"), [("base", 4), ("trigger", 3), ("network-storage", 6)])
def test_fault_index_tracks_edge_declaration_order(kind: str, expected: int) -> None:
    # Given: the failure variant including any invisible layout anchors.
    code = next(code for name, code in FENCE.findall(PAGE.read_text(encoding="utf-8")) if name == f"functions-v1-{kind}-failure")
    # When: derive zero-based fault indices from actual edge order.
    edges = [m for line in code.splitlines() if (m := EDGE.fullmatch(line))]
    indices = [index for index, edge in enumerate(edges) if edge[2] == "==>"]
    # Then: the hand-maintained supported indices still name the fault edge.
    assert indices == [expected]
