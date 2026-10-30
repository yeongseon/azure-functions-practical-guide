#!/usr/bin/env python3
"""Fixture-based contract tests; run with python3 scripts/test_diagram_inventory.py."""

import copy
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest
from collections.abc import Callable

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from scripts import diagram_inventory as inventory

try:
    import jsonschema
except ImportError:  # the scanner works without it; only the parity test needs it
    jsonschema = None

ROOT = Path(__file__).resolve().parents[1]


class ParsingTests(unittest.TestCase):
    def test_html_ancestor_makes_indented_fences_blocking(self):
        ancestors = ('<div>', '<section>', '<details>', '<aside>', '<table>\n  <td>',
                     '<custom-widget>', '<div class="x">', '<DIV>', '<div\n  class="x">')
        for ancestor in ancestors:
            for marker in ('```', '~~~'):
                for newline in ('\n', '\r\n'):
                    with self.subTest(ancestor=ancestor, marker=marker, newline=newline):
                        text = ancestor + '\n\n    Example:\n\n    ' + marker + 'mermaid\nflowchart LR\n    ' + marker + '\n</div>\n'
                        found, _, findings = inventory.scan_fences(text.replace('\n', newline))
                        self.assertEqual([item for item in found if not item.example], [])
                        self.assertEqual(findings, [{'line': len(ancestor.splitlines()) + 4, 'reason': 'indented'}])

    def test_html_wrapper_with_intervening_content_keeps_indented_fence_blocking(self):
        wrappers = (('<div>\n', '</div>\n'), ('<section>\n', '</section>\n'), ('<details>\n<summary>Title</summary>\n', '</details>\n'),
                    ('<table>\n  <tr>\n    <td>\n', '    </td>\n  </tr>\n</table>\n'), ('<custom-widget>\n', '</custom-widget>\n'))
        contents = ('', 'Explanation.\n\n', '# Heading\n\n', '- item\n\n', '---\n\n', '```bash\necho hi\n```\n\n',
                    '<section>\n\nInner.\n\n', '<!-- note -->\n\n', '![alt](x.png)\n\n', '<br>\n\n')
        for opening, closing in wrappers:
            for content in contents:
                for marker in ('```', '~~~'):
                    for prefix in ('    ', '\t'):
                        for newline in ('\n', '\r\n'):
                            with self.subTest(opening=opening, content=content, marker=marker, prefix=prefix, newline=newline):
                                tail = '</section>\n' if content.startswith('<section>') else ''
                                text = (opening + '\n' + content + prefix + marker + 'mermaid\n' + prefix + 'flowchart LR\n'
                                        + prefix + marker + '\n' + tail + closing).replace('\n', newline)
                                found, unclosed, findings = inventory.scan_fences(text)
                                line = next(n for n, row in enumerate(text.splitlines(), 1) if 'mermaid' in row)
                                self.assertEqual((found, unclosed), ([], []))
                                self.assertEqual(findings, [{'line': line, 'reason': 'indented'}])

    def test_html_context_ends_with_its_closing_tag(self):
        fence = '    ```mermaid\n    flowchart LR\n    ```\n'
        found, unclosed, findings = inventory.scan_fences('<p>\n\n' + fence + '\n</p>\n\n' + fence)
        self.assertEqual((found, unclosed), ([], []))
        self.assertEqual(findings, [{'line': 3, 'reason': 'indented'}, {'line': 9, 'reason': 'indented-code'}])
        unclosed_element = inventory.scan_fences('<p>\n\ntext\n\n' + fence)[2]
        self.assertEqual(unclosed_element, [{'line': 5, 'reason': 'indented'}])

    def test_closed_void_and_inline_html_leave_plain_code_informational(self):
        contexts = ('<br>\n\n', '<hr/>\n\n', '<img src="x.png">\n\n', '<https://example.com>\n\n', '<a href="x">Link</a>\n\n',
                    '<div>text</div>\n\n', '<div>\n\nbody\n\n</div>\n\n', '</div>\n\n', '<!DOCTYPE html>\n\n',
                    '<div>\n<section>\n\nbody\n\n</section>\n</div>\n\n', '<table>\n  <tr>\n    <td>x</td>\n  </tr>\n</table>\n\n')
        for context in contexts:
            for marker in ('```', '~~~'):
                for newline in ('\n', '\r\n'):
                    with self.subTest(context=context, marker=marker, newline=newline):
                        text = (context + '    ' + marker + 'mermaid\n    flowchart LR\n    ' + marker + '\n').replace('\n', newline)
                        found, unclosed, findings = inventory.scan_fences(text)
                        self.assertEqual((found, unclosed), ([], []))
                        self.assertEqual(findings, [{'line': len(context.splitlines()) + 1, 'reason': 'indented-code'}])

    def test_track_html_keeps_only_open_elements(self):
        cases = (([], '<div>', ['div']), ([], '<div class="x" id="y">', ['div']), ([], '<div', ['div']), ([], '   <section>', ['section']),
                 ([], '<DIV>', ['div']), ([], '<custom-widget>', ['custom-widget']), ([], '<p>text', ['p']),
                 ([], '<div/>', []), ([], '<custom-widget />', []), ([], '<br>', []), ([], '<img src="x.png">', []),
                 ([], '<span>a</span>', []), ([], '<p>text</p>', []), ([], '    <div>', []), ([], '<https://example.com>', []),
                 ([], '<a@b.c>', []), ([], '<!-- note -->', []), ([], '<!DOCTYPE html>', []), ([], 'text <div>', []),
                 (['div'], '</div>', []), (['div'], '</DIV>', []), (['div', 'section', 'p'], '</section>', ['div']),
                 (['div', 'div'], '</div>', ['div']), ([], '</div>', []), (['div'], '</section>', ['div']))
        for before, line, expected in cases:
            with self.subTest(before=before, line=line):
                stack = list(before)
                inventory.track_html(line, stack)
                self.assertEqual(stack, expected)

    def test_heading_or_thematic_break_ends_a_list_before_plain_code(self):
        fence = '    ```mermaid\n    flowchart LR\n    ```\n'
        for text, line in (('- item\n# Heading\n\n' + fence, 4), ('- item\n---\n\n' + fence, 4), ('* item\n***\n\n' + fence, 4),
                           ('1. item\n## Heading\ntext\n\n' + fence, 5), ('- item\n# Heading\n\n' + fence.replace('```', '~~~'), 4)):
            for newline in ('\n', '\r\n'):
                with self.subTest(text=text, newline=newline):
                    found, unclosed, findings = inventory.scan_fences(text.replace('\n', newline))
                    self.assertEqual((found, unclosed), ([], []))
                    self.assertEqual(findings, [{'line': line, 'reason': 'indented-code'}])

    def test_balanced_html_wrappers_block_both_fence_markers(self):
        for tag in ('div', 'section', 'details', 'aside', 'table', 'td'):
            for marker in ('```', '~~~'):
                for prefix in ('    ', '\t'):
                    for newline in ('\n', '\r\n'):
                        with self.subTest(tag=tag, marker=marker, prefix=prefix, newline=newline):
                            text = '<' + tag + '>\n\n' + prefix + marker + 'mermaid\nflowchart LR\n' + prefix + marker + '\n</' + tag + '>\n'
                            found, unclosed, findings = inventory.scan_fences(text.replace('\n', newline))
                            self.assertEqual((found, unclosed), ([], []))
                            self.assertEqual(findings, [{'line': 3, 'reason': 'indented'}])

    def test_plain_code_continuation_is_informational_and_resets_on_dedent(self):
        for before in ('', 'paragraph\n\n', '# Heading\n\n', '- item\n\nplain\n\n', '<!-- note -->\n\n'):
            for prefix in ('    ', '\t', '        '):
                for marker in ('```', '~~~'):
                    for newline in ('\n', '\r\n'):
                        with self.subTest(before=before, prefix=prefix, marker=marker, newline=newline):
                            text = before + prefix + 'Example:\n' + prefix + 'continued\n\n' + prefix + marker + 'mermaid\n' + prefix + 'flowchart LR\n' + prefix + marker + '\n\nparagraph\n    ' + marker + 'mermaid\nflowchart LR\n' + marker + '\n\n```mermaid\nflowchart LR\n```\n'
                            found, unclosed, findings = inventory.scan_fences(text.replace('\n', newline))
                            self.assertEqual([(item.body, item.example) for item in found], [('flowchart LR', False)])
                            self.assertEqual(unclosed, [])
                            self.assertEqual([item['reason'] for item in findings], ['indented-code', 'indented'])

    def test_plain_code_with_multiple_openers_has_no_blocking_findings(self):
        text = '    Example:\n    ```mermaid\n    ~~~mermaid\n    body\n    ~~~\n    ```\n'
        found, _, findings = inventory.scan_fences(text)
        self.assertEqual(found, [])
        self.assertEqual(findings, [{'line': 2, 'reason': 'indented-code'}])
        separate = '    ```mermaid\n    a\n    ```\n\n    ~~~mermaid\n    b\n    ~~~\n'
        found, _, findings = inventory.scan_fences(separate)
        self.assertEqual(found, [])
        self.assertEqual([item['reason'] for item in findings], ['indented-code', 'indented-code'])

    def test_plain_code_continuation_without_blank_before_opener(self):
        for marker in ('```', '~~~'):
            for prefix in ('    ', '\t'):
                for newline in ('\n', '\r\n'):
                    with self.subTest(marker=marker, prefix=prefix, newline=newline):
                        text = prefix + 'Example:\n' + prefix + marker + 'mermaid\n' + prefix + 'flowchart LR\n' + prefix + marker + '\n'
                        found, unclosed, findings = inventory.scan_fences(text.replace('\n', newline))
                        self.assertEqual((found, unclosed), ([], []))
                        self.assertEqual(findings, [{'line': 2, 'reason': 'indented-code'}])

    def test_indented_generic_fence_consumes_dedented_closer(self):
        for language in ('bash', '', 'python'):
            for prefix in ('    ', '\t'):
                for marker in ('```', '~~~'):
                    for newline in ('\n', '\r\n'):
                        with self.subTest(language=language, prefix=prefix, marker=marker, newline=newline):
                            text = prefix + marker + language + '\n' + prefix + 'echo hello\n' + marker + '\n\n```mermaid\nflowchart LR\nA --> B\n```\n'
                            found, unclosed, findings = inventory.scan_fences(text.replace('\n', newline))
                            self.assertEqual([(item.line, item.example, item.body) for item in found], [(5, False, 'flowchart LR\nA --> B')])
                            self.assertEqual((unclosed, findings), ([], []))

    def test_longer_outer_fence_consumes_shorter_inner_fences_to_its_closer(self):
        for char in ('`', '~'):
            for length in (3, 4, 5):
                for info in ('', 'markdown'):
                    for prefix in ('    ', '\t'):
                        for closer_prefix in ('', '  ', prefix):
                            for inner in ((char * (length - 1),) if length > 3 else ()) + (('~' if char == '`' else '`') * 3,):
                                for newline in ('\n', '\r\n'):
                                    with self.subTest(char=char, length=length, info=info, prefix=prefix, closer_prefix=closer_prefix,
                                                      inner=inner, newline=newline):
                                        text = (prefix + char * length + info + '\n' + prefix + inner + 'bash\n' + prefix + 'echo hello\n'
                                                + prefix + inner + '\n' + closer_prefix + char * length + '\n\n```mermaid\nflowchart LR\n```\n')
                                        found, unclosed, findings = inventory.scan_fences(text.replace('\n', newline))
                                        self.assertEqual([(item.line, item.example) for item in found], [(7, False)])
                                        self.assertEqual((unclosed, findings), ([], []))

    def test_same_kind_opener_of_equal_or_longer_length_still_ends_unclosed_consumption(self):
        for outer, opener in (('```', '```mermaid'), ('```', '````mermaid'), ('~~~', '~~~mermaid'), ('````', '````mermaid')):
            with self.subTest(outer=outer, opener=opener):
                text = '    ' + outer + 'bash\n    echo hello\n\n' + opener + '\nflowchart LR\n' + opener[:len(opener) - 7] + '\n'
                found, unclosed, findings = inventory.scan_fences(text)
                self.assertEqual([(item.line, item.example) for item in found], [(4, False)])
                self.assertEqual((unclosed, findings), ([], []))

    def test_indented_generic_unclosed_fence_stops_at_another_opener(self):
        text = '    ```bash\n    echo hello\n\n```mermaid\nflowchart LR\n```\n'
        found, unclosed, findings = inventory.scan_fences(text)
        self.assertEqual([(item.line, item.example) for item in found], [(4, False)])
        self.assertEqual((unclosed, findings), ([], []))

    def test_indented_list_like_code_line_is_not_a_list_item(self):
        fence = '    ```mermaid\n    flowchart LR\n    ```\n'
        found, unclosed, findings = inventory.scan_fences('    - item literal\nparagraph\n\n' + fence)
        self.assertEqual((found, unclosed), ([], []))
        self.assertEqual(findings, [{'line': 4, 'reason': 'indented-code'}])
        nested = inventory.scan_fences('- a\n    - b\nlazy\n\n' + fence)[2]
        self.assertEqual(nested, [{'line': 5, 'reason': 'indented'}])

    def test_lazy_list_paragraph_keeps_indented_fence_blocking(self):
        for marker in ('-', '*', '1.'):
            for newline in ('\n', '\r\n'):
                with self.subTest(marker=marker, newline=newline):
                    text = marker + ' item\ntext\nmore text\n\n    ```mermaid\n    flowchart LR\n    ```\n'
                    found, _, findings = inventory.scan_fences(text.replace('\n', newline))
                    self.assertEqual(found, [])
                    self.assertEqual(findings, [{'line': 5, 'reason': 'indented'}])

    def test_inline_code_comment_tokens_keep_two_visible_fences(self):
        for prose in ('Use `<!--` literally.', 'Use ``a ` <!-- -->`` here.',
                      'Use `-->` here.', 'A --> B text'):
            with self.subTest(prose=prose):
                text = prose + '\n\n' + '```mermaid\nflowchart LR\n```\n' * 2
                found, unclosed, findings = inventory.scan_fences(text)
                self.assertEqual(len(found), 2)
                self.assertEqual((unclosed, findings), ([], []))

    def test_fence_info_comment_token_has_precedence(self):
        found, unclosed, findings = inventory.scan_fences('```mermaid title="<!--"\nflowchart LR\n```\n')
        self.assertEqual(len(found), 1)
        self.assertEqual((unclosed, findings), ([], []))

    def test_comment_openers_hide_then_resume_without_headings(self):
        for opener in ('<!-- open', 'text <!-- open', '--> <!-- open'):
            with self.subTest(opener=opener):
                text = '# Visible\n' + opener + '\n# Hidden\n> ```mermaid\n> ```\n-->\n<!-- diagram-id:X -->\n```mermaid\nflowchart LR\n```\n'
                found, unclosed, findings = inventory.scan_fences(text)
                self.assertEqual([(f.diagram_id, f.headings) for f in found], [('X', ('Visible',))])
                self.assertEqual(unclosed, [])
                self.assertEqual(findings, [{'line': 4, 'reason': 'html-comment'}])

    def test_arrow_inside_hidden_fence_does_not_close_html_comment(self):
        text = 'text <!-- open\n```mermaid\nflowchart LR\nA --> B\n```\n-->\n\n```mermaid\nflowchart LR\n```\n'
        found, unclosed, findings = inventory.scan_fences(text)
        self.assertEqual([item.line for item in found], [8])
        self.assertFalse(found[0].example)
        self.assertEqual(unclosed, [])
        self.assertEqual(findings, [{'line': 2, 'reason': 'html-comment'}])

    def test_prefix_findings_consume_block_and_keep_trailing_fence(self):
        cases = [(marker + ' ', 'list-marker', '') for marker in ('-', '*', '+', '1.', '1)')]
        cases += [(prefix, 'blockquote', '') for prefix in ('> ', '> > ', '>', '> - ')]
        cases += [(prefix, 'indented', before) for prefix in ('    ', '\t')
                  for before in ('- item\n\n', '1. item\n\n', '!!! note\n\n',
                                 '??? note\n\n', '=== "A"\n\n', 'paragraph\n')]
        for prefix, reason, before in cases:
            for marker in ('```', '~~~~'):
                with self.subTest(prefix=prefix, reason=reason, before=before, marker=marker):
                    text = before + prefix + marker + 'mermaid\n  flowchart LR\n  ' + marker + '\n\n```mermaid\nflowchart LR\n```\n'
                    found, unclosed, findings = inventory.scan_fences(text)
                    self.assertEqual(len(found), 1)
                    self.assertEqual(unclosed, [])
                    self.assertEqual(findings, [{'line': len(before.splitlines()) + 1, 'reason': reason}])

    def visible_lines(self, text):
        found, unclosed, findings = inventory.scan_fences(text)
        return [item.line for item in found if not item.example], unclosed, findings

    def test_unclosed_comment_is_literal_text_that_keeps_later_diagrams(self):
        fence = '```mermaid\nflowchart LR\n```\n'
        for text, lines in (('<!-- note\n' + fence, [2]), ('text <!-- note\n' + fence + '\n' + fence, [2, 6]),
                            ('<!-- note\n```mermaid\nA-->B\n```\n', [2])):
            with self.subTest(text=text):
                self.assertEqual(self.visible_lines(text), (lines, [], []))

    def test_text_inside_a_hidden_fence_never_closes_the_comment(self):
        fence = '```mermaid\nflowchart LR\n```\n'
        self.assertEqual(self.visible_lines('<!-- note\n```bash\nA --> B\n```\n-->\n' + fence), ([6], [], []))
        self.assertEqual(self.visible_lines('<!-- note\n```bash\nA --> B\n```\n' + fence), ([5], [], []))

    def test_closed_comment_still_hides_diagrams_and_resumes_after_it(self):
        text = '<!-- note\n```mermaid\nA-->B\n```\n-->\n```mermaid\nflowchart LR\n```\n'
        self.assertEqual(self.visible_lines(text), ([6], [], [{'line': 2, 'reason': 'html-comment'}]))

    def test_unclosed_unsupported_block_never_swallows_later_diagrams(self):
        fence = '```mermaid\nflowchart LR\n```\n'
        for opener in ('> ```mermaid\n> flowchart LR\n', '- ```mermaid\n  flowchart LR\n',
                       '- item\n\n    ```mermaid\n    flowchart LR\n'):
            with self.subTest(opener=opener):
                lines, unclosed, findings = self.visible_lines(opener + '\n' + fence + '\n' + fence)
                self.assertEqual(len(lines), 2)
                self.assertEqual(unclosed, [])
                self.assertEqual(len(findings), 1)
                self.assertIn(findings[0]['reason'], inventory.BLOCKING_REASONS)

    def test_plain_indented_code_never_consumes_later_diagrams(self):
        lines, _, findings = self.visible_lines('    ```mermaid\n```mermaid\n\n```mermaid\n```\n')
        self.assertEqual(lines, [2])
        self.assertEqual(findings, [{'line': 1, 'reason': 'indented-code'}])

    def test_plain_indented_code_is_informational(self):
        for before in ('', 'paragraph\n\n', '- item\n\nplain\n\n'):
            for prefix in ('    ', '\t', '    > '):
                with self.subTest(before=before, prefix=prefix):
                    text = before + prefix + '```mermaid\n    flowchart LR\n    ```\n'
                    found, unclosed, findings = inventory.scan_fences(text)
                    self.assertEqual((found, unclosed), ([], []))
                    self.assertEqual(findings, [{'line': len(before.splitlines()) + 1, 'reason': 'indented-code'}])

    def test_container_ancestor_walk_reports_nested_indentation(self):
        text = '- item\n  paragraph\n\n      ```mermaid\n      flowchart LR\n      ```\n'
        self.assertEqual(inventory.scan_fences(text)[2], [{'line': 4, 'reason': 'indented'}])

    def test_unclosed_unsupported_block_does_not_swallow_page(self):
        text = '- ~~~~mermaid\nbody\n```mermaid\nflowchart LR\n```\n'
        found, unclosed, findings = inventory.scan_fences(text)
        self.assertEqual(len(found), 1)
        self.assertEqual(unclosed, [])
        self.assertEqual(findings, [{'line': 1, 'reason': 'list-marker'}])

    def test_long_outer_fence_has_no_findings_for_all_prefixes(self):
        body = '\n'.join(prefix + '```mermaid\n' + prefix + 'flowchart LR\n' + prefix + '```'
                         for prefix in ('- ', '* ', '+ ', '1. ', '1) ', '> ', '> > ', '>', '    > ', '    ', '\t'))
        text = '``````markdown\n<!-- open\n' + body + '\n!!! note\n??? note\n=== "A"\n``````\n'
        self.assertEqual(inventory.scan_fences(text)[1:], ([], []))

    def test_unusable_frontmatter_ids_never_attach(self):
        for entry in ({}, {'id': None}, {'id': ''}, {'id': 42}, {'id': []}, {'id': {}}, {'id': '   '}):
            with self.subTest(entry=entry):
                text = '---\ncontent_sources:\n  diagrams: ' + json.dumps([entry]) + '\n---\n```mermaid\nflowchart LR\n```\n'
                records, errors, _ = inventory.page_records('x.md', text)
                self.assertEqual(records[0]['provenance']['status'], 'missing')
                self.assertIsNone(records[0]['provenance']['declared'])
                self.assertTrue(records[0]['id_provisional'])
                self.assertEqual(records[0]['key'], 'x.md#~1')
                self.assertEqual(errors['frontmatter_entries_without_fence'], [{'page': 'x.md', 'entry': entry}])

    def test_duplicate_frontmatter_ids_keep_first_and_report_count(self):
        text = '---\ncontent_sources:\n  diagrams: [{id: x, note: first}, {id: x, note: second}, {id: x, note: third}]\n---\n<!-- diagram-id:x -->\n```mermaid\nflowchart LR\n```\n'
        records, errors, _ = inventory.page_records('x.md', text)
        self.assertEqual(records[0]['provenance']['declared'], {'id': 'x', 'note': 'first'})
        self.assertEqual(errors['frontmatter_duplicate_ids'], [{'page': 'x.md', 'id': 'x', 'count': 3}])

    def test_empty_comment_id_is_provisional(self):
        records, _, _ = inventory.page_records('x.md', '<!-- diagram-id: -->\n```mermaid\nflowchart LR\n```')
        self.assertIsNone(records[0]['diagram_id'])
        self.assertTrue(records[0]['id_provisional'])
        self.assertEqual(records[0]['key'], 'x.md#~1')

    def test_duplicate_suffix_avoids_literal_and_provisional_keys(self):
        text = ''.join(f'<!-- diagram-id:{identifier} -->\n```mermaid\nflowchart LR\n```\n'
                       for identifier in ('x', 'x', 'x~2', '~5')) + '```mermaid\nflowchart LR\n```\n'
        records, _, _ = inventory.page_records('x.md', text)
        self.assertEqual([r['key'] for r in records], ['x.md#x', 'x.md#x~3', 'x.md#x~2', 'x.md#~5', 'x.md#~5~2'])
        self.assertEqual(len({r['key'] for r in records}), len(records))

    def test_heading_preserves_attached_hash(self):
        found, _ = inventory.fences('# C#\n## Child ###\n```mermaid\nflowchart LR\n```')
        self.assertEqual(found[0].headings, ('C#', 'Child'))

    def test_backtick_info_cannot_contain_backticks(self):
        found, _ = inventory.fences('```mermaid `invalid`\nflowchart LR\n```')
        self.assertEqual(found, [])

    def test_identifier_colon_needs_no_space(self):
        found, _ = inventory.fences('<!-- diagram-id:X -->\n```mermaid\nflowchart LR\n```')
        self.assertEqual(found[0].diagram_id, 'X')

    def test_unrecognized_fences_are_reported(self):
        for prefix, reason, before, after in [
                ('', 'html-comment', '<!-- hidden\n', '-->\n'),
                ('> ', 'blockquote', '', ''),
                ('    ', 'indented', '- item\n', '')]:
            for marker in ('```', '~~~~'):
                with self.subTest(reason=reason, marker=marker):
                    records, errors, _ = inventory.page_records('x.md', before + prefix + marker + 'mermaid extra\n' + prefix + 'flowchart LR\n' + prefix + marker + '\n' + after)
                    self.assertEqual(records, [])
                    self.assertEqual(errors['unrecognized_mermaid_fences'], [{'page': 'x.md', 'line': 2 if before else 1, 'reason': reason}])

    def test_html_comment_closes_and_single_line_comment_is_unaffected(self):
        text = '<!-- hidden\n```mermaid\nflowchart LR\n```\n-->\n<!-- diagram-id:X -->\n```mermaid\nflowchart LR\n```\n'
        records, errors, _ = inventory.page_records('x.md', text)
        self.assertEqual([r['diagram_id'] for r in records], ['X'])
        self.assertEqual(len(errors['unrecognized_mermaid_fences']), 1)

    def test_outer_fence_does_not_report_container_examples(self):
        text = '`````markdown\n> ```mermaid\n    ~~~mermaid\n<!-- hidden\n`````\n<!-- diagram-id:X -->\n```mermaid\nflowchart LR\n```\n'
        records, errors, _ = inventory.page_records('x.md', text)
        self.assertEqual([r['diagram_id'] for r in records], ['X'])
        self.assertNotIn('unrecognized_mermaid_fences', errors)

    def test_indented_mermaid_prose_is_not_a_fence(self):
        records, errors, _ = inventory.page_records('x.md', '    mermaid is prose\n    ```text mermaid\n    ```mermaidx\n')
        self.assertEqual(records, [])
        self.assertNotIn('unrecognized_mermaid_fences', errors)

    def test_fence_variants(self):
        text = '# Title\n## Child\n<!-- diagram-id: x -->\n\n   ~~~~mermaid extra\nflowchart LR\nA-->B\n~~~\n~~~~~\n'
        found, errors = inventory.fences(text)
        self.assertEqual(len(found), 1)
        self.assertEqual(found[0].diagram_id, 'x')
        self.assertEqual(found[0].headings, ('Title', 'Child'))
        self.assertEqual(found[0].body, 'flowchart LR\nA-->B\n~~~')
        self.assertEqual(errors, [])

    def test_nested_example(self):
        records, _, excluded = inventory.page_records('example.md', '````markdown\n```mermaid\nflowchart LR\nA-->B\n```\n````\n')
        self.assertEqual(len(records), 1)
        self.assertEqual(excluded[0]['kind'], 'example')

    def test_unclosed(self):
        found, errors = inventory.fences('```mermaid\nflowchart LR\n')
        self.assertFalse(found[0].closed)
        self.assertEqual(errors, [1])

    def test_id_must_be_adjacent_nonblank(self):
        found, _ = inventory.fences('<!-- diagram-id: old -->\nparagraph\n```mermaid\nflowchart LR\n```')
        self.assertIsNone(found[0].diagram_id)

    def test_duplicate_ids(self):
        fence = '<!-- diagram-id: same -->\n```mermaid\nflowchart LR\n```\n'
        records, errors, _ = inventory.page_records('x.md', fence * 3)
        self.assertEqual([r['key'] for r in records], ['x.md#same', 'x.md#same~2', 'x.md#same~3'])
        self.assertEqual([r['id_provisional'] for r in records], [False, True, True])
        self.assertEqual([r['diagram_id'] for r in records], ['same'] * 3)
        self.assertEqual(errors['duplicate_ids_on_page'], [{'key': 'x.md#same', 'count': 3,
                         'keys': ['x.md#same', 'x.md#same~2', 'x.md#same~3']}])

    def test_missing_ids_use_ordinals(self):
        records, errors, _ = inventory.page_records('x.md', '```mermaid\nflowchart LR\n```\n' * 2)
        self.assertEqual([r['key'] for r in records], ['x.md#~1', 'x.md#~2'])
        self.assertTrue(all(r['id_provisional'] and r['diagram_id'] is None for r in records))
        self.assertEqual(errors['missing_id_comment'], ['x.md#~1', 'x.md#~2'])

    def test_sibling_frontmatter_metadata(self):
        text = '---\nslug: arbitrary\ncontent_sources:\n  references: [{url: example}]\n  diagrams: [{id: x, extra: [true]}]\n---\n<!-- diagram-id: x -->\n```mermaid\nflowchart LR\n```\n'
        records, errors, _ = inventory.page_records('docs/x.md', text)
        self.assertEqual(records[0]['provenance']['declared'], {'id': 'x', 'extra': [True]})
        self.assertEqual(errors, {})

    def test_verbatim_unknown_provenance(self):
        text = '---\ncontent_sources:\n  diagrams:\n    - id: x\n      source: self-generated\n      justification: "Exact  spacing"\n      future: {a: [1, true]}\n    - id: orphan\n---\n<!-- diagram-id: x -->\n```mermaid\nflowchart LR\n```'
        records, errors, _ = inventory.page_records('x.md', text)
        self.assertEqual(records[0]['provenance']['declared'], {'id': 'x', 'source': 'self-generated', 'justification': 'Exact  spacing', 'future': {'a': [1, True]}})
        self.assertEqual(errors['frontmatter_entries_without_fence'][0]['entry'], {'id': 'orphan'})

    def test_frontmatter_variants(self):
        for header, status in [('', 'missing'), ('---\ncontent_sources: []\n---\n', 'malformed'), ('---\ncontent_sources: {references: []}\n---\n', 'missing'), ('---\nx: [\n---\n', 'malformed')]:
            with self.subTest(header=header):
                records, _, _ = inventory.page_records('x.md', header + '```mermaid\nflowchart LR\n```')
                self.assertEqual(records[0]['provenance']['status'], status)

    def test_genre_signals(self):
        for body, expected in [('flowchart LR\nA-->B', 'flow'), ('graph LR\nsubgraph X\nA-->B\nend', 'topology'), ('flowchart LR\nA{Ready?} -->|Yes| B', 'decision'), ('graph LR\nsubgraph X\nA{Ready?}-->B\nend', 'unknown'), ('sequenceDiagram\nA->>B: hi', 'sequence'), ('stateDiagram-v2\nA-->B', 'state'), ('pie\n"A": 1', 'chart'), ('timeline\n2026: event', 'timeline')]:
            with self.subTest(body=body):
                self.assertEqual(inventory.classify(body)[1], expected)


class AssignmentTests(unittest.TestCase):
    def __init__(self, methodName: str = 'runTest') -> None:
        super().__init__(methodName)
        self.diagram: inventory.Record = {}
        self.rules: inventory.Record = {}

    def setUp(self) -> None:
        self.diagram = inventory.diagram_record('docs/platform/x.md', 1, inventory.Occurrence(1, 3, 'x', (), 'flowchart LR', ''))
        self.rules = {'ownership_rules': [
            {'id': 'a', 'paths': ['docs/**'], 'priority': 1, 'batch_issue': 1, 'rationale': 'platform'},
            {'id': 'b', 'paths': ['docs/platform/*'], 'priority': 2, 'batch_issue': 2, 'rationale': 'topic'}], 'overrides': {}}

    def test_priority_records_all_candidates(self):
        result, error = inventory.assign(self.diagram, self.rules)
        self.assertEqual((result['batch_issue'], result['candidates'], error), (2, ['a', 'b'], None))

    def test_equal_priority_overlap(self):
        self.rules['ownership_rules'][0]['priority'] = 2
        _, error = inventory.assign(self.diagram, self.rules)
        assert error is not None
        self.assertEqual(error['key'], 'docs/platform/x.md#x')

    def test_override_wins(self):
        self.rules['overrides'][self.diagram['key']] = {'batch_issue': 3, 'rationale': 'reviewed distinction'}
        result, error = inventory.assign(self.diagram, self.rules)
        self.assertEqual((result['batch_issue'], result['method'], error), (3, 'override', None))

    def test_explicit_residual(self):
        self.rules['ownership_rules'][1]['residual'] = True
        result, _ = inventory.assign(self.diagram, self.rules)
        self.assertEqual(result['method'], 'residual-rule')

    def test_no_match_is_error(self):
        self.rules['ownership_rules'] = []
        _, error = inventory.assign(self.diagram, self.rules)
        self.assertIsNotNone(error)


class TreeTests(unittest.TestCase):
    def __init__(self, methodName: str = 'runTest') -> None:
        super().__init__(methodName)
        self.root: Path = Path(tempfile.gettempdir())
        self.rules: inventory.Record = {}

    def setUp(self) -> None:
        temporary = tempfile.TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        self.root = Path(temporary.name)
        (self.root / 'scripts').mkdir()
        (self.root / 'docs/reference').mkdir(parents=True)
        for relative in (inventory.SCRIPT, inventory.SCHEMA):
            _ = shutil.copyfile(ROOT / relative, self.root / relative)
        self.rules = {'repository': 'fixture', 'batches': [{'issue': 1, 'title': 'Fixture', 'phase': 'P0', 'scope': 'Fixture diagrams', 'owns_diagrams': True}], 'ownership_rules': [{'id': 'fixture', 'paths': ['*.md', 'docs/**'], 'priority': 1, 'batch_issue': 1, 'rationale': 'Fixture scope'}], 'overrides': {}, 'occurrence_exclusions': [{'id': 'example', 'paths': ['example.md'], 'kind': 'example', 'reason': 'Authoring example'}], 'asset_exclusions': [{'id': 'shots', 'group': 'screenshots', 'paths': ['docs/assets/*.png'], 'reason': 'Portal capture'}], 'visuals': []}
        _ = (self.root / inventory.RULES).write_text(inventory.encoded(self.rules))
        _ = (self.root / 'docs/x.md').write_text('<!-- diagram-id: x -->\n```mermaid\nflowchart LR\nA-->B\n```\n')

    def build(self) -> inventory.Record:
        return inventory.build(self.root, self.rules, '0' * 40)

    def test_migration_states_and_exception_schema(self):
        schema = json.loads((self.root / inventory.SCHEMA).read_text())
        cases = [(state, None, state in {'not-started', 'in-progress', 'completed'}) for state in
                 ('not-started', 'in-progress', 'completed', 'exception', 'complete')]
        cases += [('exception', reason, valid) for reason, valid in
                  ((None, False), ('', False), (' \t\n', False), ('\u00a0', False),
                   ('\u2003\u202f\u3000', False), ('\u0085\u2028\u2029', False),
                   ('Owner deferred conversion', True), (42, False))]
        cases += [(state, 'Unexpected reason', False) for state in
                  ('not-started', 'in-progress', 'completed')]
        for state, reason, valid in cases:
            with self.subTest(state=state, reason=reason):
                value = self.build()
                value['diagrams'][0]['migration'] = {'state': state, 'exception': reason}
                self.assertEqual(not inventory.structural(value, schema, schema['$defs']), valid)
                if jsonschema is not None:
                    self.assertEqual(jsonschema.Draft202012Validator(schema).is_valid(value), valid)

    def test_write_preserves_migration_progress_by_key(self):
        for state, reason in (('in-progress', None), ('completed', None),
                              ('exception', 'Owner deferred conversion')):
            with self.subTest(state=state):
                previous = self.build()
                migration = {'state': state, 'exception': reason}
                previous['diagrams'][0]['migration'] = migration
                _ = (self.root / inventory.MANIFEST).write_text(inventory.encoded(previous))
                written = self.cli('--write')
                self.assertEqual(written.returncode, 0, written.stderr)
                actual = json.loads((self.root / inventory.MANIFEST).read_text())
                self.assertEqual(actual['diagrams'][0]['migration'], migration)
                checked = self.cli('--check')
                self.assertEqual(checked.returncode, 0, checked.stdout)

    def test_deleted_tracked_page_is_absent_for_write_and_verify(self):
        _ = (self.root / 'docs/second.md').write_text('# Second page\n')
        for args in (('init',), ('add', '.')):
            result = subprocess.run(['git', *args], cwd=self.root, capture_output=True, text=True)
            self.assertEqual(result.returncode, 0, result.stderr)
        initial = self.cli('--write', '--base-commit', '0' * 40)
        self.assertEqual(initial.returncode, 0, initial.stderr)
        (self.root / 'docs/x.md').unlink()
        advisory = self.cli('--verify-tree')
        self.assertEqual(advisory.returncode, 0, advisory.stderr)
        self.assertNotIn('Traceback', advisory.stderr)
        self.assertEqual(json.loads(advisory.stdout)['removed'], ['docs/x.md#x'])
        written = self.cli('--write')
        self.assertEqual(written.returncode, 0, written.stderr)
        self.assertNotIn('Traceback', written.stderr)
        self.assertEqual(json.loads((self.root / inventory.MANIFEST).read_text())['diagrams'], [])
        self.assertIn('docs/second.md', inventory.tracked(self.root))
        self.assertNotIn('docs/x.md', inventory.tracked(self.root))

    def test_walk_tracks_only_existing_files(self):
        (self.root / 'folder.md').mkdir()
        (self.root / 'dangling.md').symlink_to(self.root / 'absent.md')
        (self.root / 'docs/x.md').unlink()
        self.assertEqual(inventory.tracked(self.root), sorted(
            [inventory.SCRIPT, inventory.SCHEMA, inventory.RULES]))

    def test_asset_wildcards_require_explicit_vector_or_source_claims(self):
        directory = self.root / 'docs/assets'
        directory.mkdir()
        paths = {extension: f'docs/assets/diagram{extension}' for extension in inventory.ASSETS}
        for path in paths.values():
            _ = (self.root / path).write_text('fixture')
        rule = self.rules['asset_exclusions'][0]
        for pattern in ('docs/assets/*', 'docs/assets/diagram.?vg', 'docs/assets/diagram.[sm]*'):
            with self.subTest(pattern=pattern):
                rule['paths'] = [pattern]
                result = self.build()
                self.assertIn(paths['.svg'], result['exceptions']['unclassified_assets'])
                self.assertIn(paths['.mmd'], result['exceptions']['unclassified_assets'])
        rule['paths'] = ['docs/assets/*']
        result = self.build()
        raster = {paths[e] for e in ('.png', '.webp', '.jpg', '.jpeg', '.gif')}
        self.assertEqual(set(result['exclusions']['assets'][0]['paths']), raster)
        self.assertEqual(set(result['exceptions']['unclassified_assets']), set(paths.values()) - raster)
        rule['paths'].append(paths['.svg'])
        exact = self.build()
        self.assertEqual(set(exact['exclusions']['assets'][0]['paths']), raster | {paths['.svg']})
        self.assertIn(paths['.mmd'], exact['exceptions']['unclassified_assets'])
        rule['paths'] = ['docs/assets/*']
        rule['extensions'] = ['.svg', '.mmd']
        explicit = self.build()
        self.assertEqual(set(explicit['exclusions']['assets'][0]['paths']), raster | {paths['.svg'], paths['.mmd']})
        self.assertEqual(set(explicit['exceptions']['unclassified_assets']),
                         set(paths.values()) - raster - {paths['.svg'], paths['.mmd']})
        rule['paths'] = ['elsewhere/*']
        self.assertEqual(self.build()['exceptions']['unclassified_assets'], sorted(paths.values()))

    def test_asset_suffix_and_extension_opt_in_are_case_insensitive(self):
        (self.root / 'docs/assets').mkdir()
        paths = ['docs/assets/diagram.PNG', 'docs/assets/diagram.SVG', 'docs/assets/diagram.MMD']
        for path in paths:
            _ = (self.root / path).write_text('fixture')
        rule = self.rules['asset_exclusions'][0]
        rule['paths'] = ['docs/assets/*']
        for extensions, claimed in (([], paths[:1]), (['.svg', '.mmd'], paths),
                                     (['.SVG'], paths[:2])):
            with self.subTest(extensions=extensions):
                rule['extensions'] = extensions
                result = self.build()
                self.assertEqual(set(result['exclusions']['assets'][0]['paths']), set(claimed))
                self.assertEqual(set(result['exceptions']['unclassified_assets']), set(paths) - set(claimed))

    def test_changed_body_invalidates_review_but_preserves_plan(self):
        previous = self.build()
        prior = previous['diagrams'][0]
        prior['classification']['review_status'] = 'reviewed'
        prior.update(genre_candidate='topology', needs_review=False)
        prior['context']['reader_intent'] = 'Identify boundaries'
        prior['target']['base'] = 'Planned base'
        prior['migration'] = {'state': 'in-progress', 'exception': None}
        for changed in (False, True):
            with self.subTest(changed=changed):
                if changed:
                    _ = (self.root / 'docs/x.md').write_text(
                        '<!-- diagram-id:x -->\n```mermaid\ngraph LR\nsubgraph X\nA{Ready?}-->B\nend\n```\n')
                _ = (self.root / inventory.MANIFEST).write_text(inventory.encoded(previous))
                written = self.cli('--write')
                self.assertEqual(written.returncode, 0, written.stderr)
                actual = json.loads((self.root / inventory.MANIFEST).read_text())['diagrams'][0]
                self.assertEqual(actual['classification']['review_status'], 'unreviewed' if changed else 'reviewed')
                self.assertEqual(actual['genre_candidate'], 'unknown' if changed else 'topology')
                self.assertEqual(actual['needs_review'], changed)
                self.assertEqual(actual['context']['reader_intent'], prior['context']['reader_intent'])
                self.assertEqual(actual['target'], prior['target'])
                self.assertEqual(actual['migration'], prior['migration'])

    def assert_drift(self, expected: inventory.Record) -> None:
        empty = {name: [] for name in ('added', 'removed', 'moved', 'changed', 'reclassified',
                                      'provenance', 'relocated', 'assets', 'visuals')}
        for strict in (False, True):
            result = self.cli('--verify-tree', *(['--strict'] if strict else []))
            self.assertEqual(result.returncode, int(strict and bool(expected)), result.stderr)
            self.assertEqual(json.loads(result.stdout), {**empty, **expected})

    def test_verify_tree_provenance_drift(self):
        original = (self.root / 'docs/x.md').read_text()
        for before, after in (({'id': 'x', 'note': 'old'}, {'id': 'x', 'note': 'new'}),
                              ({'id': 'x', 'note': 'old'}, None)):
            with self.subTest(after=after):
                def page(entry: inventory.Record | None) -> str:
                    return '---\ncontent_sources:\n  diagrams: ' + json.dumps([entry] if entry else []) + '\n---\n' + original
                _ = (self.root / 'docs/x.md').write_text(page(before))
                _ = (self.root / inventory.MANIFEST).write_text(inventory.encoded(self.build()))
                _ = (self.root / 'docs/x.md').write_text(page(after))
                self.assert_drift({'provenance': ['docs/x.md#x']})

    def test_verify_tree_relocated_drift(self):
        original = (self.root / 'docs/x.md').read_text()
        for field in ('line', 'end_line', 'heading_path'):
            with self.subTest(field=field):
                baseline = self.build()
                baseline['diagrams'][0]['location'][field] = ['Former heading'] if field == 'heading_path' else 99
                _ = (self.root / inventory.MANIFEST).write_text(inventory.encoded(baseline))
                self.assert_drift({'relocated': ['docs/x.md#x']})
        _ = (self.root / 'docs/x.md').write_text('\n' + original)
        self.assert_drift({'relocated': ['docs/x.md#x']})

    def test_verify_tree_asset_drift(self):
        directory = self.root / 'docs/assets'
        directory.mkdir()
        _ = (directory / 'old.png').write_text('fixture')
        _ = (directory / 'old.svg').write_text('fixture')
        _ = (self.root / inventory.MANIFEST).write_text(inventory.encoded(self.build()))
        _ = (directory / 'old.png').rename(directory / 'new.png')
        _ = (directory / 'old.svg').rename(directory / 'new.svg')
        self.assert_drift({'assets': [
            {'group': 'screenshots', 'added': ['docs/assets/new.png'], 'removed': ['docs/assets/old.png']},
            {'group': None, 'added': ['docs/assets/new.svg'], 'removed': ['docs/assets/old.svg']}]})

    def test_verify_tree_visual_drift(self):
        visual = self.visual_manifest()['visuals'][0]
        for change in ('added', 'removed', 'changed'):
            with self.subTest(change=change):
                self.rules['visuals'] = [] if change == 'added' else [copy.deepcopy(visual)]
                _ = (self.root / inventory.MANIFEST).write_text(inventory.encoded(self.build()))
                self.rules['visuals'] = [] if change == 'removed' else [copy.deepcopy(visual)]
                if change == 'changed':
                    self.rules['visuals'][0]['sources'] = ['docs/new-graph.json']
                _ = (self.root / inventory.RULES).write_text(inventory.encoded(self.rules))
                self.assert_drift({'visuals': ['visual:x']})

    def test_asset_drift_added_and_removed_groups(self):
        previous = self.build()
        current = copy.deepcopy(previous)
        previous['exclusions']['assets'] = [
            {'group': 'old', 'paths': ['old.png']}, {'group': 'empty', 'paths': []}]
        current['exclusions']['assets'] = [{'group': 'new', 'paths': ['new.png']}]
        self.assertEqual(inventory.drift(previous, current)['assets'], [
            {'group': 'new', 'added': ['new.png'], 'removed': []},
            {'group': 'old', 'added': [], 'removed': ['old.png']}])

    def test_drift_ignores_asset_order_and_unchanged_visuals(self):
        previous = self.visual_manifest()
        previous['exclusions']['assets'][0]['paths'] = ['a.png', 'b.png']
        previous['exceptions']['unclassified_assets'] = ['a.svg', 'b.svg']
        current = copy.deepcopy(previous)
        current['exclusions']['assets'][0]['paths'].reverse()
        current['exceptions']['unclassified_assets'].reverse()
        self.assertEqual(inventory.drift(previous, current), {name: [] for name in (
            'added', 'removed', 'moved', 'changed', 'reclassified', 'provenance', 'relocated', 'assets', 'visuals')})

    def visual_manifest(self) -> inventory.Record:
        value = self.build()
        value['visuals'] = [{'key': 'visual:x', 'kind': 'cytoscape', 'pages': ['docs/x.md'],
                             'sources': ['docs/graph.json'], 'assignment': copy.deepcopy(value['diagrams'][0]['assignment']),
                             'disposition': 'migration-required', 'rationale': 'Published graph'}]
        value['totals']['non_mermaid_visuals'] = 1
        return value

    def test_visual_ownership_and_keys(self):
        baseline = self.visual_manifest()
        self.assertEqual(inventory.check(self.root, baseline, self.rules), [])
        mutations: list[tuple[str, Callable[[inventory.Record], None], str]] = [
            ('unknown-batch', lambda m: m['visuals'][0]['assignment'].update(batch_issue=999), 'invalid owning batch'),
            ('non-owning', lambda m: m['batches'][0].update(owns_diagrams=False), 'visual:x: invalid owning batch'),
            ('duplicate', lambda m: m['visuals'].append(copy.deepcopy(m['visuals'][0])), 'visuals: duplicate key'),
            ('collision', lambda m: m['visuals'][0].update(key=m['diagrams'][0]['key']), 'visuals: key collides'),
            ('count', lambda m: m['totals'].update(non_mermaid_visuals=0), 'totals.non_mermaid_visuals')]
        for name, mutate, message in mutations:
            with self.subTest(mutation=name):
                value = copy.deepcopy(baseline)
                mutate(value)
                self.assertTrue(any(message in e for e in inventory.check(self.root, value, self.rules)))

    def test_excluded_visual_schema_parity(self):
        schema = json.loads((self.root / inventory.SCHEMA).read_text())
        value = self.visual_manifest()
        value['visuals'][0].update(disposition='excluded-pending-owner-decision', rationale='Branding only')
        value['visuals'][0]['assignment'].update(method='excluded', batch_issue=None, rationale='Branding only')
        self.assertEqual(inventory.check(self.root, value, self.rules), [])
        mutations: list[Callable[[inventory.Record], None]] = [
            lambda m: m['visuals'][0]['assignment'].update(batch_issue=1),
            lambda m: m['visuals'][0].update(rationale=''),
            lambda m: m['visuals'][0]['assignment'].update(rationale=''),
            lambda m: m['visuals'][0]['assignment'].update(rationale='   ')]
        for mutate in mutations:
            with self.subTest(mutation=mutate):
                changed = copy.deepcopy(value)
                mutate(changed)
                self.assertTrue(inventory.structural(changed, schema, schema['$defs']))
                self.assertTrue(inventory.check(self.root, changed, self.rules))
                if jsonschema is not None:
                    self.assertFalse(jsonschema.Draft202012Validator(schema).is_valid(changed))

    def test_visual_disposition_is_free_text(self):
        schema = json.loads((self.root / inventory.SCHEMA).read_text())
        excluded = self.visual_manifest()
        excluded['visuals'][0]['assignment'].update(method='excluded', batch_issue=None, rationale='Owner decision pending')
        for base in (self.visual_manifest(), excluded):
            for disposition in ('excluded', 'excluded-pending-owner-decision', 'migration-required', 'other'):
                with self.subTest(method=base['visuals'][0]['assignment']['method'], disposition=disposition):
                    value = copy.deepcopy(base)
                    value['visuals'][0]['disposition'] = disposition
                    self.assertEqual(inventory.structural(value, schema, schema['$defs']), [])
                    self.assertEqual(inventory.check(self.root, value, self.rules), [])
                    if jsonschema is not None:
                        self.assertTrue(jsonschema.Draft202012Validator(schema).is_valid(value))

    def test_new_exception_schema_is_closed(self):
        schema = json.loads((self.root / inventory.SCHEMA).read_text())
        for name, entry in [('frontmatter_duplicate_ids', {'page': 'x.md', 'id': 'x', 'count': 2}),
                            ('unrecognized_mermaid_fences', {'page': 'x.md', 'line': 1, 'reason': 'blockquote'})]:
            value = self.build()
            value['exceptions'][name] = [entry]
            self.assertEqual(inventory.structural(value, schema, schema['$defs']), [])
            for changed in ({**entry, 'extra': True}, {k: v for k, v in entry.items() if k != 'page'},
                            {**entry, 'count': 1} if 'count' in entry else {**entry, 'reason': 'other'}):
                with self.subTest(name=name, entry=changed):
                    value['exceptions'][name] = [changed]
                    self.assertTrue(inventory.structural(value, schema, schema['$defs']))
                    if jsonschema is not None:
                        self.assertFalse(jsonschema.Draft202012Validator(schema).is_valid(value))

    def test_unrecognized_write_warns_check_blocks_only_rendered(self):
        for reason, text in [('html-comment', '<!-- hidden\n```mermaid\nflowchart LR\n```\n-->\n'),
                             ('indented-code', '\n    ```mermaid\n    flowchart LR\n    ```\n'),
                             ('list-marker', '- ```mermaid\n  flowchart LR\n  ```\n'),
                             ('blockquote', '> ```mermaid\n> flowchart LR\n> ```\n'),
                             ('indented', '- item\n    ```mermaid\n    flowchart LR\n    ```\n')]:
            with self.subTest(reason=reason):
                _ = (self.root / 'docs/x.md').write_text(text + text)
                written = self.cli('--write', '--base-commit', '0' * 40)
                self.assertEqual(written.returncode, 0, written.stderr)
                blocking = reason in {'blockquote', 'list-marker', 'indented'}
                self.assertEqual(len(written.stderr.splitlines()), 1 if blocking else 0)
                if blocking:
                    self.assertIn('docs/x.md:', written.stderr)
                    self.assertIn(f'({reason})', written.stderr)
                checked = self.cli('--check')
                self.assertEqual(checked.returncode, int(blocking), checked.stdout)
                self.assertIn(reason, checked.stdout)
                if blocking:
                    self.assertIn('docs/x.md:', checked.stdout)
                    self.assertIn('move the fence to the top level with at most 3 spaces of indentation, or show it inside a longer outer fence, then regenerate', checked.stdout)
                else:
                    self.assertEqual(sum(f': {reason} Mermaid fence is not rendered (informational)' in line for line in checked.stdout.splitlines()), 2)

    def test_html_container_write_records_blocking_extraction(self):
        _ = (self.root / 'docs/x.md').write_text('<div>\n\n    ~~~mermaid\nflowchart LR\n    ~~~\n</div>\n')
        written = self.cli('--write', '--base-commit', '0' * 40)
        self.assertEqual(written.returncode, 0, written.stderr)
        value = json.loads((self.root / inventory.MANIFEST).read_text())
        self.assertEqual(value['exceptions']['unrecognized_mermaid_fences'],
                         [{'page': 'docs/x.md', 'line': 3, 'reason': 'indented'}])
        checked = self.cli('--check')
        self.assertEqual(checked.returncode, 1, checked.stdout)
        self.assertIn('docs/x.md:3: indented', checked.stdout)

    def test_write_warning_lists_only_blocking_findings(self):
        _ = (self.root / 'docs/x.md').write_text('    ```mermaid\n    ```\n\n- ```mermaid\n  ```\n\n> ```mermaid\n> ```\n')
        result = self.cli('--write', '--base-commit', '0' * 40)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(len(result.stderr.splitlines()), 1)
        self.assertIn('4 (list-marker), 7 (blockquote)', result.stderr)
        self.assertNotIn('indented-code', result.stderr)

    def test_reason_enum_and_integer_schema_parity(self):
        schema = json.loads((self.root / inventory.SCHEMA).read_text())
        definitions = schema['$defs']
        for reason in ('html-comment', 'indented-code', 'indented', 'blockquote', 'list-marker', 'other'):
            entry = {'page': 'x.md', 'line': 1, 'reason': reason}
            contract = definitions['unrecognized_mermaid_fences']
            valid = reason != 'other'
            self.assertEqual(not inventory.structural(entry, contract, definitions), valid)
            if jsonschema is not None:
                self.assertEqual(jsonschema.Draft202012Validator(contract).is_valid(entry), valid)
        for value, valid in ((1, True), (1.0, True), (1.5, False), (True, False), (False, False)):
            with self.subTest(value=value):
                contract = {'type': 'integer'}
                self.assertEqual(not inventory.structural(value, contract, {}), valid)
                if jsonschema is not None:
                    self.assertEqual(jsonschema.Draft202012Validator(contract).is_valid(value), valid)

    def test_bom_preserves_frontmatter_association(self):
        _ = (self.root / 'docs/x.md').write_text('\ufeff---\ncontent_sources:\n  diagrams: [{id: x}]\n---\n<!-- diagram-id:x -->\n```mermaid\nflowchart LR\n```\n')
        self.assertEqual(self.build()['diagrams'][0]['provenance']['status'], 'declared')

    def test_non_utf8_is_recorded_like_unparseable_frontmatter(self):
        _ = (self.root / 'docs/x.md').write_bytes(b'\xff```mermaid\n')
        written = self.cli('--write', '--base-commit', '0' * 40)
        self.assertEqual(written.returncode, 0, written.stderr)
        value = json.loads((self.root / inventory.MANIFEST).read_text())
        self.assertEqual(value['diagrams'], [])
        self.assertEqual(value['exceptions']['frontmatter_unparseable'][0]['page'], 'docs/x.md')
        self.assertIn('UTF-8', value['exceptions']['frontmatter_unparseable'][0]['error'])

    def test_suffix_collision_keys_pass_check(self):
        _ = (self.root / 'docs/x.md').write_text(''.join(f'<!-- diagram-id:{identifier} -->\n```mermaid\nflowchart LR\n```\n' for identifier in ('x', 'x', 'x~2')))
        value = self.build()
        self.assertEqual(len({d['key'] for d in value['diagrams']}), 3)
        self.assertEqual(inventory.check(self.root, value, self.rules), [])

    def test_generated_tables_have_blank_before_end_and_are_idempotent(self):
        page = self.root / inventory.PAGE
        _ = page.write_text('\n'.join(f'<!-- BEGIN GENERATED: diagram-inventory:{n} -->\nstale\n<!-- END GENERATED: diagram-inventory:{n} -->' for n in ('section', 'type', 'batch', 'exclusions', 'exceptions')))
        written = self.cli('--write', '--base-commit', '0' * 40)
        self.assertEqual(written.returncode, 0, written.stderr)
        first = page.read_bytes()
        lines = page.read_text().splitlines()
        for index, line in enumerate(lines):
            if line.startswith('<!-- END GENERATED:'):
                self.assertEqual(lines[index - 1], '')
        self.assertEqual(self.cli('--check').returncode, 0)
        self.assertEqual(self.cli('--write').returncode, 0)
        self.assertEqual(page.read_bytes(), first)

    def test_tree_label_drift_is_advisory_for_check(self):
        _ = (self.root / inventory.MANIFEST).write_text(inventory.encoded(self.build()))
        path = self.root / 'docs/x.md'
        _ = path.write_text(path.read_text().replace('A-->B', 'A[Changed label]-->B'))
        checked = self.cli('--check')
        self.assertEqual(checked.returncode, 0, checked.stdout)
        advisory = self.cli('--verify-tree')
        self.assertEqual(advisory.returncode, 0)
        self.assertEqual(json.loads(advisory.stdout)['changed'], ['docs/x.md#x'])

    def cli(self, *args: str) -> subprocess.CompletedProcess[str]:
        return subprocess.run([sys.executable, str(self.root / inventory.SCRIPT), '--root', str(self.root), *args], cwd=tempfile.gettempdir(), capture_output=True, text=True, env={**os.environ, 'PYTHONDONTWRITEBYTECODE': '1'})

    def test_determinism(self):
        first = self.cli('--write', '--base-commit', '0' * 40)
        self.assertEqual(first.returncode, 0, first.stderr)
        before = (self.root / inventory.MANIFEST).read_bytes()
        second = self.cli('--write')
        self.assertEqual(second.returncode, 0, second.stderr)
        self.assertEqual(before, (self.root / inventory.MANIFEST).read_bytes())

    def test_asset_grouping_and_unclassified(self):
        (self.root / 'docs/assets').mkdir()
        _ = (self.root / 'docs/assets/a.png').write_bytes(b'fixture')
        _ = (self.root / 'loose.svg').write_text('<svg/>')
        with (self.root / 'docs/x.md').open('a') as handle:
            _ = handle.write('![shot](assets/a.png)\n![again](assets/a.png)\n')
        result = self.build()
        self.assertEqual(result['exclusions']['assets'][0]['referenced_count'], 2)
        self.assertEqual(result['exceptions']['unclassified_assets'], ['loose.svg'])

    def test_exclusion(self):
        _ = shutil.copyfile(self.root / 'docs/x.md', self.root / 'example.md')
        result = self.build()
        self.assertEqual(result['totals']['excluded_occurrences'], 1)
        self.assertEqual(result['totals']['migration_required'], 1)
        self.assertEqual(result['totals']['by_batch'], {'1': 1})
        self.assertEqual(result['batches'][0]['count'], 1)
        self.assertEqual(result['totals']['by_assignment_method'], {'excluded': 1, 'rule': 1})
        excluded: inventory.Record = next(d for d in result['diagrams'] if d['page'] == 'example.md')
        self.assertEqual(excluded['assignment'], {'batch_issue': None, 'method': 'excluded',
                         'rule': 'example', 'candidates': ['fixture'], 'rationale': 'Authoring example'})
        self.assertEqual(inventory.check(self.root, result, self.rules), [])

    def test_exclusion_key_invariant(self):
        value = self.build()
        value['exclusions']['occurrences'].append({'key': 'absent', 'kind': 'example', 'reason': 'fixture'})
        self.assertTrue(any('keys must exactly match' in e for e in inventory.check(self.root, value, self.rules)))

    def test_nested_exclusion_needs_no_owner(self):
        _ = (self.root / 'example.md').write_text('````markdown\n```mermaid\nflowchart LR\n```\n````\n')
        self.rules['ownership_rules'] = []
        (self.root / 'docs/x.md').unlink()
        value = self.build()
        self.assertEqual(value['diagrams'][0]['assignment']['rule'], 'nested-fence-example')
        self.assertEqual(value['totals']['by_batch'], {})
        self.assertEqual(inventory.check(self.root, value, self.rules), [])

    def test_duplicate_keys_pass_check(self):
        path = self.root / 'docs/x.md'
        _ = path.write_text(path.read_text() * 3)
        self.assertEqual(inventory.check(self.root, self.build(), self.rules), [])

    def test_reused_ids(self):
        _ = shutil.copyfile(self.root / 'docs/x.md', self.root / 'docs/y.md')
        self.assertEqual(self.build()['exceptions']['id_reused_on_other_pages'], {'x': ['docs/x.md', 'docs/y.md']})

    def test_preserve_reviewed_fields(self):
        previous = self.build()
        diagram: inventory.Record = previous['diagrams'][0]
        diagram['classification']['review_status'] = 'reviewed'
        diagram['genre_candidate'] = 'topology'
        diagram['context']['reader_intent'] = 'Identify boundaries'
        diagram['target']['base'] = 'Container Apps environment'
        diagram['target']['extensions'] = ['candidate']
        diagram['target']['overlays'] = ['annotation']
        diagram['needs_review'] = False
        previous['diagrams'].append({**copy.deepcopy(diagram), 'key': 'gone.md#gone'})
        _ = (self.root / inventory.MANIFEST).write_text(inventory.encoded(previous))
        outcome = self.cli('--write')
        self.assertEqual(outcome.returncode, 0, outcome.stderr)
        regenerated: inventory.Record = json.loads((self.root / inventory.MANIFEST).read_text())
        actual: inventory.Record = regenerated['diagrams'][0]
        self.assertEqual(len(regenerated['diagrams']), 1)
        self.assertEqual((actual['genre_candidate'], actual['classification']['review_status'], actual['context'], actual['target'], actual['migration']), (diagram['genre_candidate'], 'reviewed', diagram['context'], diagram['target'], diagram['migration']))
        unchanged = self.cli('--verify-tree', '--strict')
        self.assertEqual(unchanged.returncode, 0, unchanged.stdout)
        self.assertFalse(any(json.loads(unchanged.stdout).values()))

    def test_generated_blocks_write_and_check(self):
        page = self.root / inventory.PAGE
        _ = page.write_text('# Inventory\n<!-- BEGIN GENERATED: diagram-inventory:section -->\nstale\n<!-- END GENERATED: diagram-inventory:section -->\n')
        manifest = self.build()
        _ = (self.root / inventory.MANIFEST).write_text(inventory.encoded(manifest))
        stale = self.cli('--check')
        self.assertEqual(stale.returncode, 1)
        self.assertIn('stale generated blocks', stale.stdout)
        written = self.cli('--write')
        self.assertEqual(written.returncode, 0, written.stderr)
        self.assertIn('| docs-root | 1 |', page.read_text())
        self.assertNotIn('stale', page.read_text())
        checked = self.cli('--check')
        self.assertEqual(checked.returncode, 0, checked.stdout)

    def test_generated_blocks_all_tables(self):
        page = self.root / inventory.PAGE
        names = ('section', 'type', 'batch', 'exclusions', 'exceptions')
        _ = page.write_text('\n'.join(f'<!-- BEGIN GENERATED: diagram-inventory:{n} -->\nstale\n<!-- END GENERATED: diagram-inventory:{n} -->' for n in names))
        _, updated = inventory.generated_page(self.root, self.build())
        assert updated is not None
        self.assertNotIn('stale', updated)
        self.assertEqual(updated.count('| Count |'), 5)

    def test_generated_blocks_unmatched(self):
        for marker in ('BEGIN', 'END'):
            with self.subTest(marker=marker):
                _ = (self.root / inventory.PAGE).write_text(f'<!-- {marker} GENERATED: diagram-inventory:section -->')
                with self.assertRaisesRegex(inventory.InventoryError, 'unmatched generated marker section'):
                    _ = inventory.generated_page(self.root, self.build())

    def test_generated_blocks_reversed_or_repeated(self):
        begin = '<!-- BEGIN GENERATED: diagram-inventory:section -->'
        end = '<!-- END GENERATED: diagram-inventory:section -->'
        for text in (end + begin, begin + end + begin, begin + end + begin + end):
            with self.subTest(text=text):
                _ = (self.root / inventory.PAGE).write_text(text)
                with self.assertRaisesRegex(inventory.InventoryError, 'unmatched generated marker section'):
                    _ = inventory.generated_page(self.root, self.build())

    def test_generated_page_absent(self):
        self.assertEqual(inventory.generated_page(self.root, self.build()), (None, None))

    def test_compact_encoding(self):
        value = self.build()
        first = inventory.encoded(value)
        self.assertEqual(first, inventory.encoded(value))
        self.assertEqual(json.loads(first), value)
        self.assertTrue(first.endswith('\n'))
        self.assertNotIn('\r', first)
        for field in ('diagrams', 'batches', 'candidate_components'):
            for entry in value[field]:
                compact = json.dumps(entry, ensure_ascii=False, sort_keys=True, separators=(',', ':'))
                self.assertIn('    ' + compact, first.splitlines())
        self.assertLess(max(map(len, first.splitlines())), 6000)

    def test_compact_baseline_line_budget(self):
        value: inventory.Record = json.loads((ROOT / inventory.MANIFEST).read_text())
        text = inventory.encoded(value)
        self.assertLess(max(map(len, text.splitlines())), 6000)
        self.assertLess(len(text.splitlines()), 1500)
        self.assertEqual(json.loads(text), value)

    def test_check_failure_messages(self):
        baseline = self.build()
        mutations: list[tuple[str, Callable[[inventory.Record], None], str]] = [('count', lambda m: m['totals'].update(occurrences=99), 'totals.occurrences'), ('hash', lambda m: m['baseline'].update(rules_sha256='0' * 64), 'hash differs'), ('batch', lambda m: m['diagrams'][0]['assignment'].update(batch_issue=999), 'invalid owning batch'), ('key', lambda m: m['diagrams'][0].update(key='wrong'), 'key does not match')]
        for name, mutate, message in mutations:
            with self.subTest(name=name):
                value = copy.deepcopy(baseline)
                mutate(value)
                _ = (self.root / inventory.MANIFEST).write_text(inventory.encoded(value))
                result = self.cli('--check')
                self.assertEqual(result.returncode, 1)
                self.assertIn(message, result.stdout)

    def test_verify_tree_detects_drift(self):
        _ = (self.root / inventory.MANIFEST).write_text(inventory.encoded(self.build()))
        _ = (self.root / 'docs/y.md').write_text('```mermaid\nsequenceDiagram\nA->>B: hi\n```')
        result = self.cli('--verify-tree', '--strict')
        self.assertEqual(result.returncode, 1)
        self.assertEqual(json.loads(result.stdout)['added'], ['docs/y.md#~1'])

    def test_verify_tree_drift_categories(self):
        original = (self.root / 'docs/x.md').read_text()
        for name in ('removed', 'moved', 'changed', 'reclassified'):
            with self.subTest(category=name):
                path = self.root / 'docs/x.md'
                _ = path.write_text(original)
                _ = (self.root / inventory.MANIFEST).write_text(inventory.encoded(self.build()))
                if name == 'removed':
                    path.unlink()
                elif name == 'moved':
                    _ = path.rename(self.root / 'docs/new.md')
                elif name == 'changed':
                    _ = path.write_text(original.replace('A-->B', 'A-->C'))
                else:
                    _ = path.write_text(original.replace('flowchart LR\nA-->B', 'sequenceDiagram\nA->>B: hi'))
                outcome = self.cli('--verify-tree', '--strict')
                self.assertEqual(outcome.returncode, 1, outcome.stderr)
                difference: inventory.Record = json.loads(outcome.stdout)
                expected = [{'from': 'docs/x.md#x', 'to': 'docs/new.md#x'}] if name == 'moved' else ['docs/x.md#x']
                self.assertEqual(difference[name], expected)
                moved = self.root / 'docs/new.md'
                if moved.exists():
                    moved.unlink()

    @unittest.skipIf(jsonschema is None, 'jsonschema is not installed')
    def test_schema_mutation_parity(self):
        assert jsonschema is not None
        schema: inventory.Record = json.loads((self.root / inventory.SCHEMA).read_text())
        validator = jsonschema.Draft202012Validator(schema)
        baseline: inventory.Record = json.loads((ROOT / inventory.MANIFEST).read_text())
        self.assertEqual(inventory.structural(baseline, schema, schema['$defs']), [])
        self.assertTrue(validator.is_valid(baseline))
        mutations: list[tuple[str, Callable[[inventory.Record], None]]] = [
            ('wrong-type', lambda m: m['diagrams'][0].update(ordinal='1')),
            ('missing-key', lambda m: m['diagrams'][0].pop('context')),
            ('extra-key', lambda m: m['diagrams'][0]['location'].update(extra=True)),
            ('genre', lambda m: m['diagrams'][0].update(genre_candidate='verified')),
            ('method', lambda m: m['diagrams'][0]['classification'].update(method='verified')),
            ('review', lambda m: m['diagrams'][0]['classification'].update(review_status='approved')),
            ('hash', lambda m: m['baseline']['scanner'].update(sha256='bad')),
            ('commit', lambda m: m['baseline'].update(base_commit='bad')),
            ('null-owner', lambda m: next(d for d in m['diagrams'] if d['assignment']['method'] != 'excluded')['assignment'].update(batch_issue=None)),
            ('excluded-owner', lambda m: next(d for d in m['diagrams'] if d['assignment']['method'] == 'excluded')['assignment'].update(batch_issue=407)),
            ('provenance', lambda m: m['diagrams'][0]['provenance'].update(status='verified')),
            ('verification', lambda m: m['diagrams'][0]['provenance'].update(verification='verified')),
            ('migration', lambda m: m['diagrams'][0]['migration'].update(state='complete')),
            ('target', lambda m: m['diagrams'][0]['target'].update(status='accepted')),
            ('exception', lambda m: m['exceptions']['frontmatter_unparseable'].append({'page': 'x', 'error': 2})),
            ('negative-count', lambda m: m['totals'].update(occurrences=-1)),
            ('bool-integer', lambda m: m.update(schema_version=True)),
        ]
        for name, mutate in mutations:
            with self.subTest(mutation=name):
                value = copy.deepcopy(baseline)
                mutate(value)
                self.assertTrue(inventory.structural(value, schema, schema['$defs']))
                self.assertFalse(validator.is_valid(value))

    def test_builtin_structural_validation(self):
        schema: inventory.Record = json.loads((self.root / inventory.SCHEMA).read_text())
        value = self.build()
        value['diagrams'][0]['classification']['method'] = 'verified'
        errors = inventory.structural(value, schema, schema['$defs'])
        self.assertTrue(any('invalid enum' in error for error in errors))


class IntegrationTests(unittest.TestCase):
    def test_current_tree_reproduction_requires_opt_in(self):
        reproduction = type(self).test_baseline_reproduction_in_temp_tree
        self.assertEqual(getattr(reproduction, '__unittest_skip__', False),
                         os.environ.get('DIAGRAM_INVENTORY_REPRODUCE') != '1')

    def test_baseline_check(self):
        if not (ROOT / inventory.MANIFEST).exists():
            self.skipTest('baseline not generated yet')
        manifest: inventory.Record = json.loads((ROOT / inventory.MANIFEST).read_text())
        rules: inventory.Record = json.loads((ROOT / inventory.RULES).read_text())
        self.assertEqual(inventory.check(ROOT, manifest, rules), [])

    @unittest.skipUnless(os.environ.get('DIAGRAM_INVENTORY_REPRODUCE') == '1',
                         'current-tree reproduction is opt-in: baseline is frozen at baseline.base_commit; tree drift is advisory')
    def test_baseline_reproduction_in_temp_tree(self):
        if not (ROOT / inventory.MANIFEST).exists():
            self.skipTest('baseline not generated yet')
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            paths = [p for p in inventory.tracked(ROOT) if p.endswith('.md') or Path(p).suffix.lower() in inventory.ASSETS]
            paths += [inventory.SCRIPT, inventory.RULES, inventory.SCHEMA, inventory.MANIFEST]
            for relative in paths:
                destination = root / relative
                destination.parent.mkdir(parents=True, exist_ok=True)
                _ = shutil.copyfile(ROOT / relative, destination)
            result = subprocess.run([sys.executable, str(root / inventory.SCRIPT), '--write'], capture_output=True, text=True)
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertEqual((root / inventory.MANIFEST).read_bytes(), (ROOT / inventory.MANIFEST).read_bytes())


if __name__ == '__main__':
    _ = unittest.main(verbosity=2)
