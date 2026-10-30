#!/usr/bin/env python3
"""Inventory tracked diagrams without rendering or verifying declared sources.

Usage: python3 scripts/diagram_inventory.py --write [--base-commit SHA]
       python3 scripts/diagram_inventory.py --check | --verify-tree | --summary
Paths are relative to this script's repository, never the caller's directory.
Node/edge/component extraction is approximate; genres are candidates only.
"""

from __future__ import annotations

import argparse
import collections
import copy
import fnmatch
import hashlib
import json
import re
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any, TypeAlias
from urllib.parse import unquote, urlsplit

import yaml

# Heterogeneous JSON and verbatim foreign YAML do not share a recursive record shape.
Record: TypeAlias = dict[str, Any]
VERSION = '1.1.0'
MANIFEST = 'docs/reference/diagram-manifest.json'
SCHEMA = 'docs/reference/diagram-manifest.schema.json'
RULES = 'scripts/diagram_inventory_rules.json'
SCRIPT = 'scripts/diagram_inventory.py'
PAGE = 'docs/reference/diagram-inventory.md'
FENCE = re.compile(r'^ {0,3}(`{3,}|~{3,})(.*)$')
IDENTIFIER = re.compile(r'^\s*<!--\s*diagram-id:\s*(.*?)\s*-->\s*$')
HEADING = re.compile(r'^ {0,3}(#{1,6})[ \t]+(.*?)[ \t]*$')
LIST_MARKER = re.compile(r'(?:[-+*]|\d{1,9}[.)])(?:[ \t]+|$)')
CONTAINER = re.compile(r'^\s*(!!!|\?\?\?\+?|===[+!]?)\s')
THEMATIC_BREAK = re.compile(r'^ {0,3}([-*_])(?:[ \t]*\1){2,}[ \t]*$')
HTML_OPEN = re.compile(r'^ {0,3}<([A-Za-z][A-Za-z0-9-]*)(?=[\s/>]|$)')
HTML_CLOSE = re.compile(r'^ {0,3}</([A-Za-z][A-Za-z0-9-]*)\s*>')
HTML_VOID = frozenset('area base br col embed hr img input link meta param source track wbr'.split())
INLINE_CODE = re.compile(r'(?<!`)(`+)(?!`).*?(?<!`)\1(?!`)')
BLOCKING_REASONS = {'blockquote', 'list-marker', 'indented'}
TYPES = set(('flowchart graph sequenceDiagram stateDiagram stateDiagram-v2 '
             'gantt timeline pie quadrantChart classDiagram erDiagram journey '
             'mindmap xychart-beta block-beta gitGraph requirementDiagram '
             'C4Context sankey-beta').split())
ASSETS = {'.png', '.webp', '.jpg', '.jpeg', '.gif', '.svg', '.drawio', '.mmd',
          '.mermaid', '.puml', '.plantuml', '.excalidraw'}
RASTER_ASSETS = {'.png', '.webp', '.jpg', '.jpeg', '.gif'}
EMPTY_TARGET: Record = {'base': None, 'extensions': [], 'overlays': [], 'status': 'provisional'}


class InventoryError(Exception):
    """A named inventory contract failure suitable for CLI output."""


class StringDateLoader(yaml.SafeLoader):
    """Preserve YAML date scalars as strings for JSON interchange."""


StringDateLoader.yaml_implicit_resolvers = {
    key: [(tag, pattern) for tag, pattern in resolvers
          if tag != 'tag:yaml.org,2002:timestamp']
    for key, resolvers in yaml.SafeLoader.yaml_implicit_resolvers.items()
}


def encoded(value: Any) -> str:
    """Indent summaries; compact entries except asset groups exceeding the line budget."""
    compact_lists = {'diagrams', 'batches', 'candidate_components', 'visuals'}

    def render(item: Any, depth: int, path: tuple[str, ...]) -> str:
        pad = '  ' * depth
        if isinstance(item, dict) and item:
            fields = [json.dumps(key, ensure_ascii=False) + ': ' +
                      render(child, depth + 1, (*path, key))
                      for key, child in sorted(item.items())]
            return '{\n' + ',\n'.join('  ' + pad + field for field in fields) + '\n' + pad + '}'
        if isinstance(item, list) and item:
            compact = bool(path) and (path[-1] in compact_lists or path[0] in {'exceptions', 'exclusions'})
            entries = [json.dumps(child, ensure_ascii=False, sort_keys=True, separators=(',', ':'))
                       if compact else render(child, depth + 1, path) for child in item]
            if compact and any(len(entry) > 5900 for entry in entries):
                entries = [render(child, depth + 1, path) if len(entry) > 5900 else entry
                           for child, entry in zip(item, entries)]
            if path and path[-1] == 'paths':
                packed: list[str] = []
                for entry in entries:
                    if packed and len(packed[-1]) + len(entry) < 5800:
                        packed[-1] += ',' + entry
                    else:
                        packed.append(entry)
                entries = packed
            return '[\n' + ',\n'.join('  ' + pad + entry for entry in entries) + '\n' + pad + ']'
        return json.dumps(item, ensure_ascii=False, sort_keys=True, separators=(',', ':'))

    return render(value, 0, ()) + '\n'


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def local(root: Path, relative: str) -> Path:
    """Reject traversal and symlinks that would read outside the repository."""
    path = root / relative
    if not path.resolve().is_relative_to(root.resolve()):
        raise InventoryError(f'path outside repository: {relative}')
    return path


def tracked(root: Path) -> list[str]:
    """Use Git's index only in a repository root; fixture trees use a walk."""
    if (root / '.git').exists():
        result = subprocess.run(['git', 'ls-files', '-z'], cwd=root,
                                check=True, capture_output=True)
        return sorted(p for p in result.stdout.decode().split('\0')
                      if p and local(root, p).is_file())
    return sorted(p.relative_to(root).as_posix() for p in root.rglob('*')
                  if '.git' not in p.parts and local(root, p.relative_to(root).as_posix()).is_file())


def frontmatter(text: str) -> tuple[list[Any], int, str | None]:
    """Return canonical diagram entries, body offset, and a parse/shape error."""
    lines = text.splitlines()
    if not lines or lines[0].strip() != '---':
        return [], 0, None
    end = next((i for i in range(1, len(lines)) if lines[i].strip() == '---'), None)
    if end is None:
        return [], 0, 'unclosed frontmatter'
    try:
        data = yaml.load('\n'.join(lines[1:end]), Loader=StringDateLoader)
    except yaml.YAMLError as error:
        return [], end + 1, str(error)
    if not isinstance(data, dict):
        return [], end + 1, 'frontmatter is not a mapping'
    sources = data.get('content_sources')
    if sources is None:
        return [], end + 1, None
    if not isinstance(sources, dict):
        return [], end + 1, 'content_sources is not a mapping'
    entries = sources.get('diagrams', [])
    if not isinstance(entries, list):
        return [], end + 1, 'content_sources.diagrams is not a list'
    return entries, end + 1, None


@dataclass(frozen=True, slots=True)
class Occurrence:
    """One fence, including examples and incomplete fences, in source order."""

    line: int
    end_line: int
    diagram_id: str | None
    headings: tuple[str, ...]
    body: str
    lead_in: str
    example: bool = False
    closed: bool = True


def preceding(lines: list[str], start: int, floor: int) -> tuple[str | None, str]:
    """ID adjacency ignores blanks; lead-in skips headings and HTML comments."""
    i = start - 1
    while i >= floor and not lines[i].strip():
        i -= 1
    match = IDENTIFIER.fullmatch(lines[i]) if i >= floor else None
    identifier = (match.group(1).strip() or None) if match else None
    if match:
        i -= 1
    while i >= floor and (not lines[i].strip() or lines[i].lstrip().startswith('<!--')):
        i -= 1
    paragraph: list[str] = []
    while i >= floor and lines[i].strip():
        if HEADING.match(lines[i]) or FENCE.match(lines[i]):
            break
        paragraph.append(lines[i].strip())
        i -= 1
    lead = ' '.join(' '.join(reversed(paragraph)).split())[:200]
    lead = re.sub(r'[\w.+-]+@[\w.-]+\.[A-Za-z]{2,}', '[email omitted]', lead)
    lead = re.sub(r'\b[0-9a-fA-F]{8}(?:-[0-9a-fA-F]{4}){3}-[0-9a-fA-F]{12}\b',
                  '[identifier omitted]', lead)
    return identifier, lead


def closing(line: str, marker: str) -> bool:
    return bool(re.fullmatch(r' {0,3}' + re.escape(marker[0]) +
                             '{' + str(len(marker)) + r',}\s*', line))


def fences(text: str, offset: int = 0) -> tuple[list[Occurrence], list[int]]:
    """Parse CommonMark fence boundaries; nested Mermaid is excluded example text."""
    output, unclosed, _ = scan_fences(text, offset)
    return output, unclosed


def prefixed_fence(line: str) -> tuple[str, bool, bool]:
    """Strip whitespace, quote and list tokens without interpreting their nesting."""
    rest = line.expandtabs(4)
    quote = listed = False
    while rest:
        rest = rest.lstrip(' ')
        if rest.startswith('>'):
            quote = True
            rest = rest[1:]
            continue
        marker = LIST_MARKER.match(rest)
        if marker:
            listed = True
            rest = rest[marker.end():]
            continue
        break
    return rest, quote, listed


def mermaid_opener(line: str) -> re.Match[str] | None:
    opening = FENCE.match(line)
    if opening:
        marker, info = opening.groups()
        if info.strip().split()[:1] == ['mermaid'] and not (marker[0] == '`' and '`' in info):
            return opening
    return None


def indentation(line: str) -> int:
    expanded = line.expandtabs(4)
    return len(expanded) - len(expanded.lstrip(' '))


def track_html(line: str, open_tags: list[str]) -> None:
    """Keep the names of HTML elements that a line start opened and nothing has closed yet.

    Void and self-closing tags and elements closed on the same line are ignored; a closing tag
    pops the nearest open element of that name. An element that is never closed stays open,
    which only makes a later indented fence blocking instead of informational.
    """
    closing_tag = HTML_CLOSE.match(line)
    if closing_tag:
        name = closing_tag.group(1).lower()
        if name in open_tags:
            del open_tags[len(open_tags) - 1 - open_tags[::-1].index(name):]
        return
    opening_tag = HTML_OPEN.match(line)
    if not opening_tag:
        return
    name = opening_tag.group(1).lower()
    rest = line[opening_tag.end():]
    tag_end = rest.find('>')
    if name in HTML_VOID or (tag_end > 0 and rest[tag_end - 1] == '/') or f'</{name}' in rest.lower():
        return
    open_tags.append(name)


def plain_code(lines: list[str], index: int, html_open: bool) -> bool:
    """A blank/start boundary outside open HTML and without a container ancestor is code."""
    column = indentation(lines[index])
    if html_open or column < 4 or (index and lines[index - 1].strip()):
        return False
    for position in range(index - 1, -1, -1):
        earlier = lines[position]
        if not earlier.strip() or indentation(earlier) >= column:
            continue
        column = indentation(earlier)
        if LIST_MARKER.match(earlier.lstrip()) or CONTAINER.match(earlier):
            return False
        if column == 0:
            while position and lines[position - 1].strip():
                if HEADING.match(lines[position]) or THEMATIC_BREAK.match(lines[position]):
                    break
                position -= 1
                if indentation(lines[position]) < 4 and LIST_MARKER.match(lines[position].lstrip()):
                    return False
            break
    return True


def unsupported_fence(line: str, plain: bool) -> tuple[str, str] | None:
    """Report opener-like lines conservatively, distinguishing plain code."""
    rest, quote, listed = prefixed_fence(line)
    opening = mermaid_opener(rest)
    if not opening:
        return None
    reason = 'indented'
    if plain:
        reason = 'indented-code'
    elif quote:
        reason = 'blockquote'
    elif listed:
        reason = 'list-marker'
    return reason, opening.group(1)


def unsupported_end(lines: list[str], index: int, marker: str) -> int:
    """Skip an unsupported block to its closing marker.

    A shorter fence of the same kind inside it is content. Another opener of the same
    kind and at least the same length means the block is unclosed, so the scan resumes after its opener.
    """
    for end in range(index + 1, len(lines)):
        rest = re.sub(r'^[\s>]*', '', lines[end])
        if closing(rest, marker):
            return end + 1
        opener = FENCE.match(rest)
        if opener and opener.group(1)[0] == marker[0] and len(opener.group(1)) >= len(marker):
            break
    return index + 1


def opens_comment(line: str) -> bool:
    """Inline code is literal; prefixed container comments are not modeled."""
    rest, quote, listed = prefixed_fence(line)
    if quote or listed:
        return False
    literal_free = INLINE_CODE.sub('', rest)
    opener = literal_free.find('<!--')
    return opener >= 0 and '-->' not in literal_free[opener + 4:]


def comment_end(lines: list[str], start: int) -> tuple[int, list[int]] | None:
    """Find the line closing a comment opened at start, or None: the site shows an unclosed one as text.

    The site extracts fences before it reads comments, so text inside any fence never closes a comment.
    """
    hidden: list[int] = []
    i = start + 1
    while i < len(lines):
        rest = prefixed_fence(lines[i])[0]
        opening = FENCE.match(rest)
        if opening:
            if mermaid_opener(rest):
                hidden.append(i + 1)
            i = unsupported_end(lines, i, opening.group(1))
            continue
        if '-->' in lines[i]:
            return i, hidden
        i += 1
    return None


def scan_fences(text: str, offset: int = 0, example: bool = False) -> tuple[list[Occurrence], list[int], list[Record]]:
    """Consume comments/fences atomically; examples never emit unsupported findings.

    Plain code starts only at a blank/start boundary outside open HTML elements and without
    container ancestors, survives blank/indented lines, and ends before the first nonblank dedent.
    Every unsupported fence (any language) consumes its closer before resuming;
    only Mermaid openers emit findings. A new same-kind opener stops unclosed consumption.
    """
    lines = text.splitlines()
    headings: list[tuple[int, str]] = []
    output: list[Occurrence] = []
    unclosed: list[int] = []
    unrecognized: list[Record] = []
    open_tags: list[str] = []
    i = offset
    plain = False
    while i < len(lines):
        if lines[i].strip() and indentation(lines[i]) < 4:
            plain = False
        if not plain:
            plain = plain_code(lines, i, bool(open_tags))
        heading = HEADING.match(lines[i])
        opening = FENCE.match(lines[i])
        unsupported = unsupported_fence(lines[i], plain)
        if not example and not opening and opens_comment(lines[i]):
            closed = comment_end(lines, i)
            if closed:
                end, hidden = closed
                unrecognized.extend({'line': n, 'reason': 'html-comment'} for n in hidden)
                i = end + 1
                continue
        prefixed = FENCE.match(prefixed_fence(lines[i])[0])
        if prefixed and not opening and not example:
            if unsupported:
                reason, _ = unsupported
                unrecognized.append({'line': i + 1, 'reason': reason})
            end = unsupported_end(lines, i, prefixed.group(1))
            if any(line.strip() and indentation(line) < 4 for line in lines[i + 1:end]):
                plain = False
            i = end
            continue
        if not opening:
            if heading:
                level = len(heading.group(1))
                headings = [h for h in headings if h[0] < level]
                title = re.sub(r'[ \t]+#+[ \t]*$', '', heading.group(2))
                headings.append((level, title))
            track_html(lines[i], open_tags)
            i += 1
            continue
        marker, info = opening.groups()
        if marker[0] == '`' and '`' in info:
            i += 1
            continue
        language = info.strip().split()[0] if info.strip() else ''
        end = next((j for j in range(i + 1, len(lines)) if closing(lines[j], marker)), len(lines))
        if end == len(lines):
            unclosed.append(i + 1)
        if language == 'mermaid':
            identifier, lead = preceding(lines, i, offset)
            output.append(Occurrence(i + 1, min(end + 1, len(lines)), identifier,
                                     tuple(h[1] for h in headings), '\n'.join(lines[i + 1:end]),
                                     lead, closed=end < len(lines)))
        else:
            nested, _, _ = scan_fences('\n'.join(lines[i + 1:end]), example=True)
            for item in nested:
                output.append(Occurrence(item.line + i + 1, item.end_line + i + 1,
                                         item.diagram_id, tuple(h[1] for h in headings),
                                         item.body, item.lead_in, True, item.closed))
        i = end + 1
    return output, unclosed, unrecognized


def classify(body: str) -> tuple[str, str, Record]:
    """Classify syntax, not intent; mixed decision/topology signals stay unknown."""
    source = '\n'.join(line for line in body.splitlines() if not line.strip().startswith('%%'))
    words = source.split()
    kind = words[0] if words and words[0] in TYPES else 'unknown'
    signals = {
        'subgraphs': len(re.findall(r'^\s*subgraph\b', source, re.M)),
        'decision_nodes': len(re.findall(r'\b\w+\s*\{[^{}]+\}', source)),
        'yes_no_labels': len(re.findall(r'(?:\|\s*|--\s*)(?:yes|no)\s*(?:\||--)', source, re.I)),
    }
    genre = {'sequenceDiagram': 'sequence', 'stateDiagram': 'state', 'stateDiagram-v2': 'state',
             'gantt': 'timeline', 'timeline': 'timeline', 'pie': 'chart',
             'quadrantChart': 'chart', 'xychart-beta': 'chart'}.get(kind, 'unknown')
    method = 'syntax'
    if kind in {'flowchart', 'graph'}:
        method = 'heuristic'
        decision = signals['decision_nodes'] or signals['yes_no_labels']
        genre = 'unknown' if decision and signals['subgraphs'] else (
            'decision' if decision else ('topology' if signals['subgraphs'] else 'flow'))
    return kind, genre, {'method': method, 'signals': signals, 'review_status': 'unreviewed'}


def labels(body: str) -> set[str]:
    """Approximate node labels, counted once per diagram rather than per node."""
    found = re.findall(r'\b[\w-]+\s*\[\[?\s*"?([^\]\n]+?)"?\s*\]\]?', body)
    return {re.sub(r'\s+', ' ', re.sub(r'<[^>]+>', ' ', s)).strip(' "').lower()
            for s in found if 2 < len(s) < 100}


def matches(rule: Record, diagram: Record) -> bool:
    """Path globs and optional topic regex are conjunctive; globs are alternatives."""
    path_match = any(fnmatch.fnmatchcase(diagram['page'], pattern)
                     for pattern in rule.get('paths', []))
    topic = ' '.join([diagram['page'], *diagram['location']['heading_path'],
                      diagram['context']['lead_in']])
    return path_match and bool(re.search(rule.get('topic_regex', ''), topic, re.I))


def assign(diagram: Record, rules: Record) -> tuple[Record, Record | None]:
    """Record all matches; override, then highest priority, never file order."""
    candidates = [r for r in rules['ownership_rules'] if matches(r, diagram)]
    candidate_ids = sorted(r['id'] for r in candidates)
    override = rules.get('overrides', {}).get(diagram['key'])
    chosen = override
    method = 'override'
    if chosen is None and candidates:
        priority = max(r['priority'] for r in candidates)
        winners = [r for r in candidates if r['priority'] == priority]
        if len({r['batch_issue'] for r in winners}) == 1:
            chosen = sorted(winners, key=lambda r: r['id'])[0]
            method = 'residual-rule' if chosen.get('residual', False) else 'rule'
    if chosen is None:
        return {'batch_issue': None, 'method': 'rule', 'rule': None,
                'candidates': candidate_ids, 'rationale': 'Unassigned or tied highest priorities'}, {
                    'key': diagram['key'], 'candidates': candidate_ids}
    return {'batch_issue': chosen['batch_issue'], 'method': method,
            'rule': chosen.get('id', 'reviewed-override'), 'candidates': candidate_ids,
            'rationale': chosen['rationale']}, None


def diagram_record(page: str, ordinal: int, item: Occurrence) -> Record:
    kind, genre, classification = classify(item.body)
    published = page.startswith('docs/')
    section = page.split('/')[1] if published and page.count('/') > 1 else (
        'docs-root' if published else 'repository')
    return {
        'key': f'{page}#{item.diagram_id or "~" + str(ordinal)}',
        'diagram_id': item.diagram_id, 'id_provisional': item.diagram_id is None,
        'page': page, 'section': section, 'published': published, 'ordinal': ordinal,
        'location': {'line': item.line, 'end_line': item.end_line, 'heading_path': list(item.headings)},
        'mermaid_type': kind, 'genre_candidate': genre, 'classification': classification,
        'needs_review': genre == 'unknown', 'context': {'lead_in': item.lead_in, 'reader_intent': None},
        'baseline': {'source_sha256': hashlib.sha256(item.body.encode()).hexdigest(),
                     'lines': len(item.body.splitlines()), 'subgraphs': classification['signals']['subgraphs'],
                     'nodes_approx': len(labels(item.body)),
                     'edges_approx': len(re.findall(r'-->|---|==>|-\.->|->>|-->>', item.body))},
        'target': copy.deepcopy(EMPTY_TARGET), 'migration': {'state': 'not-started', 'exception': None},
    }


def unique_record_keys(records: list[Record]) -> list[str]:
    """Reserve literal IDs before allocating collision suffixes in source order."""
    bases = [f'{r["page"]}#{r["diagram_id"] or "~" + str(r["ordinal"])}' for r in records]
    reserved = set(bases)
    used: set[str] = set()
    keys: list[str] = []
    for base in bases:
        key = base
        suffix = 2
        if key in used:
            key = f'{base}~{suffix}'
            while key in reserved or key in used:
                suffix += 1
                key = f'{base}~{suffix}'
        used.add(key)
        keys.append(key)
    return keys


def page_records(page: str, text: str) -> tuple[list[Record], Record, list[Record]]:
    entries, offset, error = frontmatter(text)
    occurrences, unclosed, unrecognized = scan_fences(text, offset)
    records = [diagram_record(page, ordinal, item) for ordinal, item in enumerate(occurrences, 1)]
    exceptions: collections.defaultdict[str, list[Any]] = collections.defaultdict(list)
    exclusions: list[Record] = []
    declared_by_id: Record = {}
    entry_ids: collections.Counter[str] = collections.Counter()
    for entry in entries:
        identifier = entry.get('id') if isinstance(entry, dict) else None
        if isinstance(identifier, str) and identifier.strip():
            entry_ids[identifier] += 1
            declared_by_id.setdefault(identifier, entry)
    for identifier, count in sorted(entry_ids.items()):
        if count > 1:
            exceptions['frontmatter_duplicate_ids'].append({'page': page, 'id': identifier, 'count': count})
    if unrecognized:
        exceptions['unrecognized_mermaid_fences'] = [{'page': page, **item} for item in unrecognized]
    if error:
        exceptions['frontmatter_unparseable'].append({'page': page, 'error': error})
    for line in unclosed:
        exceptions['unclosed_fences'].append({'page': page, 'line': line})
    for item, record, key in zip(occurrences, records, unique_record_keys(records)):
        record['id_provisional'] = record['id_provisional'] or record['key'] != key
        record['key'] = key
        declared = declared_by_id.get(item.diagram_id) if item.diagram_id else None
        status = 'declared' if declared is not None else ('malformed' if error else 'missing')
        record['provenance'] = {'status': status, 'declared': declared, 'verification': 'not-performed'}
        if item.diagram_id is None:
            exceptions['missing_id_comment'].append(record['key'])
        if declared is None:
            exceptions['fences_without_frontmatter_entry'].append(record['key'])
        if item.example:
            exclusions.append({'key': record['key'], 'kind': 'example', 'reason': 'Mermaid example nested inside another code fence'})
    ids = collections.Counter(r['diagram_id'] for r in records if r['diagram_id'])
    for identifier, count in sorted(ids.items()):
        if count > 1:
            exceptions['duplicate_ids_on_page'].append({
                'key': f'{page}#{identifier}', 'count': count,
                'keys': [r['key'] for r in records if r['diagram_id'] == identifier]})
    for entry in entries:
        identifier = entry.get('id') if isinstance(entry, dict) else None
        if not isinstance(identifier, str) or not identifier.strip() or identifier not in ids:
            exceptions['frontmatter_entries_without_fence'].append({'page': page, 'entry': entry})
    return records, dict(exceptions), exclusions


def claims_asset(rule: Record, path: str) -> bool:
    """Wildcard exclusions need explicit extension opt-in for vector/source assets."""
    extension = Path(path).suffix.lower()
    for pattern in rule['paths']:
        exact = not any(character in pattern for character in '*?[') and pattern == path
        if exact or (fnmatch.fnmatchcase(path, pattern) and (
                extension in RASTER_ASSETS or extension in [e.lower() for e in rule.get('extensions', [])])):
            return True
    return False


def asset_groups(root: Path, files: list[str], rules: Record) -> tuple[list[Record], list[str]]:
    references: collections.Counter[str] = collections.Counter()
    for page in files:
        if not page.endswith('.md'):
            continue
        try:
            text = local(root, page).read_text(encoding='utf-8-sig')
        except UnicodeDecodeError:
            continue
        for destination in re.findall(r'!\[[^\]]*\]\(\s*<?([^\s)>]+)', text):
            url = urlsplit(destination)
            if url.scheme or url.netloc:
                continue
            path = root / 'docs' / unquote(url.path).lstrip('/') if url.path.startswith('/') else (
                root / page).parent / unquote(url.path)
            if path.resolve().is_relative_to(root.resolve()):
                references[path.resolve().relative_to(root.resolve()).as_posix()] += 1
    groups: list[Record] = []
    assigned: set[str] = set()
    assets = [p for p in files if Path(p).suffix.lower() in ASSETS]
    for rule in rules.get('asset_exclusions', []):
        paths = sorted(p for p in assets if p not in assigned and claims_asset(rule, p))
        assigned.update(paths)
        groups.append({'group': rule['group'], 'reason': rule['reason'], 'rule': rule['id'],
                       'count': len(paths), 'referenced_count': sum(references[p] for p in paths), 'paths': paths})
    return groups, sorted(set(assets) - assigned)


def totals(diagrams: list[Record], exclusions: list[Record], visuals: list[Record]) -> Record:
    result: Record = {'occurrences': len(diagrams), 'published': sum(d['published'] for d in diagrams),
              'repository_only': sum(not d['published'] for d in diagrams),
              'excluded_occurrences': len(exclusions), 'migration_required': len(diagrams) - len(exclusions),
              'non_mermaid_visuals': len(visuals)}
    for name, values in {
        'by_section': [d['section'] for d in diagrams],
        'by_mermaid_type': [d['mermaid_type'] for d in diagrams],
        'by_genre_candidate': [d['genre_candidate'] for d in diagrams],
        'by_batch': [str(d['assignment']['batch_issue']) for d in diagrams
                     if d['assignment']['method'] != 'excluded'],
        'by_provenance_status': [d['provenance']['status'] for d in diagrams],
        'by_assignment_method': [d['assignment']['method'] for d in diagrams],
    }.items():
        result[name] = dict(sorted(collections.Counter(values).items()))
    return result


def preserve(current: Record, previous: Record) -> None:
    """Keep human-reviewed interpretation while refreshing observed source facts."""
    old = {d['key']: d for d in previous.get('diagrams', [])}
    for diagram in current['diagrams']:
        prior = old.get(diagram['key'])
        if prior is None:
            continue
        if (prior['baseline']['source_sha256'] == diagram['baseline']['source_sha256'] and
                prior['classification']['review_status'] != 'unreviewed'):
            diagram['classification']['review_status'] = prior['classification']['review_status']
            diagram['genre_candidate'] = prior['genre_candidate']
            diagram['needs_review'] = prior['needs_review']
        diagram['context']['reader_intent'] = prior['context']['reader_intent']
        for field in ('target', 'migration'):
            diagram[field] = copy.deepcopy(prior[field])
    current['totals'] = totals(current['diagrams'], current['exclusions']['occurrences'], current['visuals'])


def build(root: Path, rules: Record, base_commit: str) -> Record:
    files = tracked(root)
    diagrams: list[Record] = []
    exclusions: list[Record] = []
    names = ('missing_id_comment duplicate_ids_on_page frontmatter_entries_without_fence '
             'fences_without_frontmatter_entry frontmatter_unparseable unresolved_overlaps '
             'unclassified_assets unclosed_fences frontmatter_duplicate_ids unrecognized_mermaid_fences').split()
    exceptions: Record = {name: [] for name in names}
    components: collections.Counter[str] = collections.Counter()
    for page in files:
        if not page.endswith('.md'):
            continue
        try:
            text = local(root, page).read_text(encoding='utf-8-sig')
        except UnicodeDecodeError as error:
            exceptions['frontmatter_unparseable'].append({'page': page, 'error': f'Invalid UTF-8: {error}'})
            continue
        records, errors, examples = page_records(page, text)
        diagrams.extend(records)
        exclusions.extend(examples)
        for name, values in errors.items():
            exceptions[name].extend(values)
        for item, diagram in zip(fences(text, frontmatter(text)[1])[0], records):
            if diagram['mermaid_type'] in {'flowchart', 'graph'}:
                components.update(labels(item.body))
    for diagram in diagrams:
        diagram['assignment'], error = assign(diagram, rules)
        exclusion = next((e for e in exclusions if e['key'] == diagram['key']), None)
        exclusion_id = 'nested-fence-example'
        for rule in rules.get('occurrence_exclusions', []):
            if matches(rule, diagram) and exclusion is None:
                exclusion = {'key': diagram['key'], 'kind': rule['kind'], 'reason': rule['reason']}
                exclusions.append(exclusion)
                exclusion_id = rule['id']
        if exclusion is not None:
            diagram['assignment'].update(batch_issue=None, method='excluded',
                                         rule=exclusion_id, rationale=exclusion['reason'])
        elif error:
            exceptions['unresolved_overlaps'].append(error)
    reused: collections.defaultdict[str, set[str]] = collections.defaultdict(set)
    for diagram in diagrams:
        if diagram['diagram_id']:
            reused[diagram['diagram_id']].add(diagram['page'])
    exceptions['id_reused_on_other_pages'] = {k: sorted(v) for k, v in sorted(reused.items()) if len(v) > 1}
    assets, exceptions['unclassified_assets'] = asset_groups(root, files, rules)
    result: Record = {'schema_version': 1, 'kind': 'diagram-inventory', 'repository': rules['repository'],
              'baseline': {'base_commit': base_commit,
                           'scanner': {'path': SCRIPT, 'version': VERSION, 'sha256': digest(local(root, SCRIPT))},
                           'rules_sha256': digest(local(root, RULES)),
                             'counting_policy': 'Every Mermaid fence in a tracked Markdown file is one occurrence; an asset referenced N times is one asset with N usages; two fences with equal text are two occurrences. Counts by batch include only Mermaid migration-required occurrences; excluded occurrences have no owning batch. Non-Mermaid visuals are reported separately and never included in totals.by_batch. Node, edge and component counts are regex approximations.'},
              'diagrams': sorted(diagrams, key=lambda d: d['key']),
              'exclusions': {'occurrences': sorted(exclusions, key=lambda e: e['key']), 'assets': assets},
              'visuals': rules.get('visuals', []), 'exceptions': exceptions,
              'candidate_components': [{'label': label, 'diagram_count': count, 'method': 'regex-approximate'}
                                       for label, count in sorted(components.items(), key=lambda p: (-p[1], p[0]))[:40]]}
    result['totals'] = totals(diagrams, exclusions, result['visuals'])
    result['batches'] = [{**batch, 'count': result['totals']['by_batch'].get(str(batch['issue']), 0)}
                         for batch in rules['batches']]
    return result


def structural(value: Any, schema: Record, definitions: Record, path: str = '$') -> list[str]:
    """Dependency-free checks for the schema vocabulary used by this contract."""
    if '$ref' in schema:
        return structural(value, definitions[schema['$ref'].split('/')[-1]], definitions, path)
    types = {'object': dict, 'array': list, 'string': str, 'integer': (int, float),
             'boolean': bool, 'null': type(None), 'number': (int, float)}
    wanted = schema.get('type')
    allowed: list[str] = wanted if isinstance(wanted, list) else [wanted] if wanted else []
    if wanted and not any(isinstance(value, types[t]) and not (
            t in {'integer', 'number'} and isinstance(value, bool)) and not (
            t == 'integer' and isinstance(value, float) and not value.is_integer()) for t in allowed):
        return [f'{path}: expected {wanted}']
    errors: list[str] = []
    if 'oneOf' in schema:
        count = sum(not structural(value, branch, definitions, path) for branch in schema['oneOf'])
        if count != 1:
            errors.append(f'{path}: expected exactly one matching oneOf branch')
    if 'if' in schema:
        branch = 'else' if structural(value, schema['if'], definitions, path) else 'then'
        errors.extend(structural(value, schema.get(branch, {}), definitions, path))
    if 'const' in schema and value != schema['const']:
        errors.append(f'{path}: expected constant {schema["const"]}')
    if 'enum' in schema and value not in schema['enum']:
        errors.append(f'{path}: invalid enum {value!r}')
    if isinstance(value, dict):
        for key in schema.get('required', []):
            if key not in value:
                errors.append(f'{path}: missing required key {key}')
        properties = schema.get('properties', {})
        for key, child in value.items():
            child_schema = properties.get(key, schema.get('additionalProperties', {}))
            if child_schema is False:
                errors.append(f'{path}: unexpected key {key}')
            elif isinstance(child_schema, dict):
                errors.extend(structural(child, child_schema, definitions, f'{path}.{key}'))
    if isinstance(value, list):
        for i, child in enumerate(value):
            errors.extend(structural(child, schema.get('items', {}), definitions, f'{path}[{i}]'))
    if isinstance(value, str):
        if 'pattern' in schema and not re.search(schema['pattern'], value):
            errors.append(f'{path}: pattern mismatch')
        if len(value) > schema.get('maxLength', len(value)):
            errors.append(f'{path}: too long')
    if isinstance(value, (int, float)) and value < schema.get('minimum', value):
        errors.append(f'{path}: below minimum')
    return errors


def generated_tables(manifest: Record) -> dict[str, str]:
    tables: dict[str, str] = {}
    for name, counts in [('section', manifest['totals']['by_section']),
                         ('type', manifest['totals']['by_mermaid_type']),
                         ('batch', manifest['totals']['by_batch']),
                         ('exclusions', {a['group']: a['count'] for a in manifest['exclusions']['assets']}),
                         ('exceptions', {k: len(v) for k, v in manifest['exceptions'].items()})]:
        tables[name] = '| ' + name.title() + ' | Count |\n|---|---:|\n' + '\n'.join(
            f'| {key} | {count} |' for key, count in sorted(counts.items())) + '\n\n'
    return tables


def generated_page(root: Path, manifest: Record) -> tuple[str | None, str | None]:
    path = local(root, PAGE)
    if not path.exists():
        return None, None
    original = path.read_text(encoding='utf-8')
    updated = original
    for name, table in generated_tables(manifest).items():
        begin = f'<!-- BEGIN GENERATED: diagram-inventory:{name} -->'
        end = f'<!-- END GENERATED: diagram-inventory:{name} -->'
        if (updated.count(begin) != updated.count(end) or updated.count(begin) > 1 or
                (begin in updated and updated.index(begin) > updated.index(end))):
            raise InventoryError(f'{PAGE}: unmatched generated marker {name}')
        updated = re.sub(re.escape(begin) + r'.*?' + re.escape(end),
                         lambda _: begin + '\n' + table + end, updated, flags=re.S)
    return original, updated


def check(root: Path, manifest: Record, rules: Record) -> list[str]:
    schema: Record = json.loads(local(root, SCHEMA).read_text())
    errors = structural(manifest, schema, schema.get('$defs', {}))
    try:
        import jsonschema
    except ImportError:
        jsonschema = None
    if jsonschema is not None:
        errors.extend(f'schema {list(e.path)}: {e.message}' for e in
                      jsonschema.Draft202012Validator(schema).iter_errors(manifest))
    if errors:
        return errors
    diagrams: list[Record] = manifest['diagrams']
    keys = [d['key'] for d in diagrams]
    if len(set(keys)) != len(keys):
        errors.append('diagrams: duplicate key')
    ordered = sorted(diagrams, key=lambda d: (d['page'], d['ordinal']))
    for diagram, expected in zip(ordered, unique_record_keys(ordered)):
        if diagram['key'] != expected:
            errors.append(f'{diagram["key"]}: key does not match page/id/ordinal')
    for key in rules.get('overrides', {}):
        if key not in keys:
            errors.append(f'override references absent key: {key}')
    batches = {b['issue']: b for b in manifest['batches']}
    visual_keys = [v['key'] for v in manifest['visuals']]
    if len(set(visual_keys)) != len(visual_keys):
        errors.append('visuals: duplicate key')
    if set(visual_keys) & set(keys):
        errors.append('visuals: key collides with diagram key')
    excluded = [e['key'] for e in manifest['exclusions']['occurrences']]
    assigned_excluded = {d['key'] for d in diagrams if d['assignment']['method'] == 'excluded'}
    if len(excluded) != len(set(excluded)) or set(excluded) != assigned_excluded or not set(excluded) <= set(keys):
        errors.append('exclusions.occurrences: keys must exactly match excluded assignments')
    for diagram in [*diagrams, *manifest['visuals']]:
        if diagram['assignment']['method'] == 'excluded':
            continue
        batch = batches.get(diagram['assignment']['batch_issue'])
        if batch is None or not batch['owns_diagrams']:
            errors.append(f'{diagram["key"]}: invalid owning batch {diagram["assignment"]["batch_issue"]}')
    computed = totals(diagrams, manifest['exclusions']['occurrences'], manifest['visuals'])
    if sum(computed['by_batch'].values()) != computed['migration_required']:
        errors.append('totals.by_batch: sum must equal migration_required')
    for name, value in computed.items():
        if manifest['totals'].get(name) != value:
            errors.append(f'totals.{name}: does not reconcile with diagrams')
    for batch in manifest['batches']:
        if batch['count'] != computed['by_batch'].get(str(batch['issue']), 0):
            errors.append(f'batch {batch["issue"]}: count does not reconcile')
    for field, file in [('rules_sha256', RULES), ('scanner', SCRIPT)]:
        observed = manifest['baseline'][field]
        if field == 'scanner':
            observed = observed['sha256']
        if observed != digest(local(root, file)):
            errors.append(f'baseline.{field}: hash differs from {file}; regenerate')
    if manifest['exceptions']['unresolved_overlaps']:
        errors.append('exceptions.unresolved_overlaps: assignments unresolved')
    for item in manifest['exceptions']['unrecognized_mermaid_fences']:
        if item['reason'] in BLOCKING_REASONS:
            errors.append(f'{item["page"]}:{item["line"]}: {item["reason"]} Mermaid fence makes inventory incomplete; move the fence to the top level with at most 3 spaces of indentation, or show it inside a longer outer fence, then regenerate')
    original, updated = generated_page(root, manifest)
    if original != updated:
        errors.append(f'{PAGE}: stale generated blocks')
    return errors


def asset_drift(previous: Record, current: Record) -> list[Record]:
    """Compare group path sets; a null group identifies unclassified assets."""
    old: dict[str | None, set[str]] = {group['group']: set(group['paths'])
                                     for group in previous['exclusions']['assets']}
    new: dict[str | None, set[str]] = {group['group']: set(group['paths'])
                                     for group in current['exclusions']['assets']}
    groups = sorted(group for group in old.keys() | new.keys() if group is not None)
    old[None] = set(previous['exceptions']['unclassified_assets'])
    new[None] = set(current['exceptions']['unclassified_assets'])
    return [{'group': group, 'added': sorted(new.get(group, set()) - old.get(group, set())),
             'removed': sorted(old.get(group, set()) - new.get(group, set()))}
            for group in [*groups, None] if old.get(group, set()) != new.get(group, set())]


def drift(previous: Record, current: Record) -> Record:
    """Compare source facts, separately reporting moves and changed classifications."""
    old: dict[str, Record] = {d['key']: d for d in previous['diagrams']}
    new: dict[str, Record] = {d['key']: d for d in current['diagrams']}
    added, removed = sorted(new.keys() - old.keys()), sorted(old.keys() - new.keys())
    moved: list[dict[str, str]] = []
    for key in removed[:]:
        matches_new = [k for k in added if new[k]['baseline']['source_sha256'] == old[key]['baseline']['source_sha256']]
        if len(matches_new) == 1:
            destination = matches_new[0]
            moved.append({'from': key, 'to': destination})
            added.remove(destination)
            removed.remove(key)
    changed = [key for key in sorted(old.keys() & new.keys())
               if old[key]['baseline']['source_sha256'] != new[key]['baseline']['source_sha256']]
    reclassified = [key for key in sorted(old.keys() & new.keys())
                    if any(old[key][f] != new[key][f] for f in ('genre_candidate', 'mermaid_type', 'assignment'))]
    provenance = [key for key in sorted(old.keys() & new.keys())
                  if old[key]['provenance'] != new[key]['provenance']]
    relocated = [key for key in sorted(old.keys() & new.keys())
                 if old[key]['location'] != new[key]['location']]
    old_visuals = {v['key']: v for v in previous['visuals']}
    new_visuals = {v['key']: v for v in current['visuals']}
    visuals = [key for key in sorted(old_visuals.keys() | new_visuals.keys())
               if old_visuals.get(key) != new_visuals.get(key)]
    return {'added': added, 'removed': removed, 'moved': moved, 'changed': changed,
            'reclassified': reclassified, 'provenance': provenance, 'relocated': relocated,
            'assets': asset_drift(previous, current), 'visuals': visuals}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    modes = parser.add_mutually_exclusive_group(required=True)
    for mode in ('write', 'check', 'verify-tree', 'summary'):
        _ = modes.add_argument('--' + mode, action='store_true')
    _ = parser.add_argument('--base-commit')
    _ = parser.add_argument('--strict', action='store_true')
    _ = parser.add_argument('--root', type=Path, default=Path(__file__).resolve().parents[1])
    args = parser.parse_args()
    root: Path = args.root.resolve()
    try:
        rules: Record = json.loads(local(root, RULES).read_text())
        path = local(root, MANIFEST)
        previous: Record = json.loads(path.read_text()) if path.exists() else {}
        if args.check:
            errors = check(root, previous, rules)
            for item in previous.get('exceptions', {}).get('unrecognized_mermaid_fences', []):
                if item['reason'] not in BLOCKING_REASONS:
                    print(f'{item["page"]}:{item["line"]}: {item["reason"]} Mermaid fence is not rendered (informational)')
            print('\n'.join(errors) if errors else 'diagram inventory: check passed')
            return int(bool(errors))
        if args.summary:
            print(encoded(previous['totals']), end='')
            return 0
        commit: str | None = args.base_commit or previous.get('baseline', {}).get('base_commit')
        if not commit:
            commit = subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=root, text=True).strip()
        if not re.fullmatch('[0-9a-f]{40}', commit):
            raise InventoryError('base_commit must be 40 lowercase hex characters')
        current = build(root, rules, commit)
        preserve(current, previous)
        if args.verify_tree:
            difference = drift(previous, current)
            print(encoded(difference), end='')
            return int(args.strict and any(difference.values()))
        errors = check(root, current, rules)
        errors = [e for e in errors if 'stale generated blocks' not in e and 'Mermaid fence makes inventory incomplete' not in e]
        if errors:
            raise InventoryError('\n'.join(errors))
        blocking = [item for item in current['exceptions']['unrecognized_mermaid_fences']
                    if item['reason'] in BLOCKING_REASONS]
        pages = sorted({item['page'] for item in blocking})
        for page in pages:
            details = ', '.join(f'{item["line"]} ({item["reason"]})' for item in blocking if item['page'] == page)
            print(f'diagram inventory: warning: {page}: unrecognized Mermaid fences at {details}; see manifest exceptions', file=sys.stderr)
        _ = path.write_text(encoded(current), encoding='utf-8', newline='\n')
        original, updated = generated_page(root, current)
        if original != updated:
            assert updated is not None
            _ = local(root, PAGE).write_text(updated, encoding='utf-8', newline='\n')
        print(f'wrote {MANIFEST}: {len(current["diagrams"])} occurrences')
        return 0
    except (InventoryError, OSError, json.JSONDecodeError, subprocess.CalledProcessError) as error:
        print(f'diagram inventory: {error}', file=sys.stderr)
        return 1


if __name__ == '__main__':
    sys.exit(main())
