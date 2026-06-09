#!/usr/bin/env python3
"""
MSLearn URL Validation Script

Validates all Microsoft Learn URLs in content_sources frontmatter across docs.
Checks for:
- HTTP 200 status (URL exists)
- Redirects (reports canonical URL)
- 404 errors (broken links)

Usage:
    python scripts/validate_mslearn_urls.py [--fix] [--verbose]

Options:
    --fix       Automatically replace redirected URLs with canonical versions
    --verbose   Show all URLs being checked, not just errors
"""

import os
import sys
import re
import argparse
import time
from pathlib import Path
from typing import Any, Dict, Iterable, List, Tuple, Optional
from concurrent.futures import ThreadPoolExecutor, as_completed

try:
    import requests
except ImportError:
    print("Error: requests library required. Install with: pip install requests")
    sys.exit(1)

try:
    import yaml
except ImportError:
    print("Error: PyYAML library required. Install with: pip install pyyaml")
    sys.exit(1)


# Rate limiting settings
REQUEST_DELAY = 0.25  # seconds between completed requests
MAX_WORKERS = 3  # parallel requests
MAX_RETRIES = 3


def extract_frontmatter(content: str) -> Optional[dict]:
    """Extract YAML frontmatter from markdown content."""
    match = re.match(r"^---\s*\n(.*?)\n---\s*\n", content, re.DOTALL)
    if not match:
        return None
    try:
        return yaml.safe_load(match.group(1))
    except yaml.YAMLError:
        return None


def add_mslearn_url(urls: set, url: Any) -> None:
    """Add a Microsoft Learn URL to the set when the value is URL-like."""
    if isinstance(url, str) and "learn.microsoft.com" in url:
        urls.add(url)


def add_mslearn_urls(urls: set, values: Any) -> None:
    """Add one URL or an iterable of URLs."""
    if isinstance(values, str):
        add_mslearn_url(urls, values)
    elif isinstance(values, Iterable):
        for value in values:
            add_mslearn_url(urls, value)


# Reference-list sub-keys in dict-form content_sources. All semantically equivalent;
# 'references' is the canonical key (see Phase 2d schema normalization plan).
# Legacy aliases (sources, text, documents) are accepted during the migration window.
REFERENCE_SUBKEYS = ("references", "sources", "text", "documents")


def iter_reference_items(content_sources: Any) -> Iterable[dict]:
    """
    Yield reference-list dict items from content_sources frontmatter.

    Supports both list-form content_sources (legacy) and dict-form with any of
    the known reference sub-key aliases. Items under unknown sub-keys are
    skipped.

    >>> list(iter_reference_items({'references': [{'url': 'a'}]}))
    [{'url': 'a'}]
    >>> list(iter_reference_items({'sources': [{'url': 'b'}]}))
    [{'url': 'b'}]
    >>> list(iter_reference_items({'text': [{'url': 'c'}]}))
    [{'url': 'c'}]
    >>> list(iter_reference_items({'documents': [{'url': 'd'}]}))
    [{'url': 'd'}]
    >>> list(iter_reference_items([{'url': 'e'}, {'url': 'f'}]))
    [{'url': 'e'}, {'url': 'f'}]
    >>> list(iter_reference_items({'unknown_key': [{'url': 'z'}]}))
    []
    >>> list(iter_reference_items({}))
    []
    >>> list(iter_reference_items(None))
    []
    >>> sorted(item['url'] for item in iter_reference_items({'references': [{'url': 'a'}], 'sources': [{'url': 'b'}]}))
    ['a', 'b']
    """
    if isinstance(content_sources, list):
        for item in content_sources:
            if isinstance(item, dict):
                yield item
    elif isinstance(content_sources, dict):
        for key in REFERENCE_SUBKEYS:
            items = content_sources.get(key)
            if isinstance(items, list):
                for item in items:
                    if isinstance(item, dict):
                        yield item


def iter_diagram_items(content_sources: Any) -> Iterable[dict]:
    """
    Yield diagram dict items from content_sources frontmatter.

    Diagrams only appear under dict-form content_sources.diagrams.

    >>> list(iter_diagram_items({'diagrams': [{'id': 'foo'}]}))
    [{'id': 'foo'}]
    >>> list(iter_diagram_items({'references': [{'url': 'a'}]}))
    []
    >>> list(iter_diagram_items([{'url': 'a'}]))
    []
    >>> list(iter_diagram_items(None))
    []
    >>> list(iter_diagram_items({}))
    []
    """
    if isinstance(content_sources, dict):
        diagrams = content_sources.get("diagrams")
        if isinstance(diagrams, list):
            for item in diagrams:
                if isinstance(item, dict):
                    yield item


def extract_mslearn_urls(frontmatter: dict) -> List[str]:
    """Extract all MSLearn URLs from content_sources in frontmatter.

    Deduplicates URLs and returns deterministic sorted order.
    Supports list-form and dict-form content_sources. All four reference
    sub-key aliases (references, sources, text, documents) are accepted
    during the Phase 2d schema migration window.

    >>> extract_mslearn_urls({'content_sources': {'references': [{'url': 'https://learn.microsoft.com/a'}]}})
    ['https://learn.microsoft.com/a']
    >>> extract_mslearn_urls({'content_sources': {'sources': [{'url': 'https://learn.microsoft.com/b'}]}})
    ['https://learn.microsoft.com/b']
    >>> extract_mslearn_urls({'content_sources': {'text': [{'url': 'https://learn.microsoft.com/c'}]}})
    ['https://learn.microsoft.com/c']
    >>> extract_mslearn_urls({'content_sources': {'documents': [{'url': 'https://learn.microsoft.com/d'}]}})
    ['https://learn.microsoft.com/d']
    >>> extract_mslearn_urls({'content_sources': [{'url': 'https://learn.microsoft.com/e'}]})
    ['https://learn.microsoft.com/e']
    >>> extract_mslearn_urls({'content_sources': {'diagrams': [{'based_on': ['https://learn.microsoft.com/f']}]}})
    ['https://learn.microsoft.com/f']
    >>> extract_mslearn_urls({'content_sources': {'references': [{'url': 'https://example.com/skip-non-mslearn'}]}})
    []
    >>> extract_mslearn_urls({})
    []
    >>> extract_mslearn_urls({'content_sources': {'references': [{'url': 'https://learn.microsoft.com/g'}], 'diagrams': [{'based_on': ['https://learn.microsoft.com/g']}]}})
    ['https://learn.microsoft.com/g']
    """
    urls = set()
    content_sources = frontmatter.get("content_sources")

    for item in iter_reference_items(content_sources):
        add_mslearn_url(urls, item.get("url"))
        add_mslearn_url(urls, item.get("mslearn_url"))
        add_mslearn_urls(urls, item.get("based_on", []))

    for diagram in iter_diagram_items(content_sources):
        add_mslearn_url(urls, diagram.get("mslearn_url"))
        add_mslearn_urls(urls, diagram.get("based_on", []))

    return sorted(urls)


def extract_source_section_urls(content: str) -> List[str]:
    """Extract MSLearn URLs from ## Sources section."""
    urls = set()

    # Find Sources section
    sources_match = re.search(
        r"^## Sources\s*\n(.*?)(?=^## |\Z)", content, re.MULTILINE | re.DOTALL
    )
    if sources_match:
        sources_text = sources_match.group(1)
        # Find all learn.microsoft.com URLs
        url_pattern = r'https://learn\.microsoft\.com/[^\s\)>\]"\']*'
        for url in re.findall(url_pattern, sources_text):
            urls.add(url.rstrip(".,;:"))

    return list(urls)


def check_url(
    url: str, session: requests.Session
) -> Tuple[str, int, str, Optional[str]]:
    """
    Check a URL and return (url, status_code, status, redirect_url).

    Returns:
        - url: Original URL
        - status_code: HTTP status code
        - status: 'ok', 'redirect', 'error', 'timeout'
        - redirect_url: Final URL if redirected, None otherwise
    """
    last_status = 0

    for attempt in range(MAX_RETRIES + 1):
        try:
            # Use HEAD first, fall back to GET if needed.
            response = session.head(url, allow_redirects=True, timeout=10)

            # Some servers don't support HEAD.
            if response.status_code == 405:
                response = session.get(url, allow_redirects=True, timeout=10)

            last_status = response.status_code

            if response.status_code == 429:
                retry_after = response.headers.get("Retry-After")
                if attempt < MAX_RETRIES:
                    delay = (
                        float(retry_after)
                        if retry_after and retry_after.isdigit()
                        else 2**attempt
                    )
                    time.sleep(delay)
                    continue
                return (url, response.status_code, "rate_limited", None)

            final_url = response.url

            if response.status_code == 200:
                if final_url != url:
                    return (url, response.status_code, "redirect", final_url)
                return (url, response.status_code, "ok", None)
            elif response.status_code == 404:
                return (url, response.status_code, "error", None)
            else:
                return (url, response.status_code, "error", None)

        except requests.Timeout:
            if attempt < MAX_RETRIES:
                time.sleep(2**attempt)
                continue
            return (url, last_status, "timeout", None)
        except requests.RequestException as e:
            if attempt < MAX_RETRIES:
                time.sleep(2**attempt)
                continue
            return (url, last_status, "error", str(e))

    return (url, last_status, "error", None)


def find_docs_files(docs_dir: Path) -> List[Path]:
    """Find all markdown files in docs directory."""
    return list(docs_dir.glob("**/*.md"))


def validate_project(
    project_path: Path, verbose: bool = False, fix: bool = False
) -> Dict:
    """
    Validate all MSLearn URLs in a project.

    Returns dict with:
        - total_urls: Total unique URLs checked
        - ok: URLs that returned 200
        - redirects: URLs that redirected (with canonical URL)
        - errors: URLs that failed (404, timeout, etc.)
        - files_checked: Number of files checked
    """
    docs_dir = project_path / "docs"
    if not docs_dir.exists():
        return {"error": f"docs directory not found: {docs_dir}"}

    results = {
        "total_urls": 0,
        "ok": [],
        "redirects": [],
        "errors": [],
        "rate_limited": [],
        "files_checked": 0,
        "files_with_urls": {},
    }

    # Collect all URLs with their source files
    url_to_files: Dict[str, List[str]] = {}

    md_files = find_docs_files(docs_dir)
    results["files_checked"] = len(md_files)

    for md_file in md_files:
        try:
            content = md_file.read_text(encoding="utf-8")
        except Exception as e:
            if verbose:
                print(f"  Warning: Could not read {md_file}: {e}")
            continue

        frontmatter = extract_frontmatter(content)
        urls = []

        if frontmatter:
            urls.extend(extract_mslearn_urls(frontmatter))

        urls.extend(extract_source_section_urls(content))

        for url in urls:
            if url not in url_to_files:
                url_to_files[url] = []
            url_to_files[url].append(str(md_file.relative_to(project_path)))

    results["total_urls"] = len(url_to_files)
    results["files_with_urls"] = url_to_files

    if not url_to_files:
        return results

    # Check URLs with rate limiting
    session = requests.Session()
    session.headers.update({"User-Agent": "MSLearn-URL-Validator/1.0"})

    print(f"  Checking {len(url_to_files)} unique URLs...")

    checked = 0
    with ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
        futures = {
            executor.submit(check_url, url, session): url for url in url_to_files.keys()
        }

        for future in as_completed(futures):
            url, status_code, status, redirect_url = future.result()
            checked += 1

            if status == "ok":
                results["ok"].append(url)
                if verbose:
                    print(f"    [OK] {url}")
            elif status == "redirect":
                results["redirects"].append(
                    {
                        "original": url,
                        "canonical": redirect_url,
                        "files": url_to_files[url],
                    }
                )
                print(f"    [REDIRECT] {url}")
                print(f"             -> {redirect_url}")
            elif status == "rate_limited":
                results["rate_limited"].append(
                    {"url": url, "status_code": status_code, "files": url_to_files[url]}
                )
                print(f"    [RATE LIMITED {status_code}] {url}")
                for f in url_to_files[url]:
                    print(f"             in: {f}")
            else:
                results["errors"].append(
                    {"url": url, "status_code": status_code, "files": url_to_files[url]}
                )
                print(f"    [ERROR {status_code}] {url}")
                for f in url_to_files[url]:
                    print(f"             in: {f}")

            # Progress indicator
            if checked % 20 == 0:
                print(f"  Progress: {checked}/{len(url_to_files)} URLs checked")

            time.sleep(REQUEST_DELAY)

    return results


def main():
    parser = argparse.ArgumentParser(
        description="Validate MSLearn URLs in documentation"
    )
    parser.add_argument("--fix", action="store_true", help="Auto-fix redirected URLs")
    parser.add_argument("--verbose", "-v", action="store_true", help="Show all URLs")
    parser.add_argument("--project", "-p", type=str, help="Specific project to check")
    parser.add_argument(
        "--all-siblings",
        action="store_true",
        help="Validate every azure-*-practical-guide sibling checkout",
    )
    args = parser.parse_args()

    repo_root = Path(__file__).parent.parent
    github_dir = repo_root.parent

    if args.project:
        project_path = Path(args.project)
        if not project_path.exists():
            project_path = github_dir / args.project
        projects = [project_path]
    elif args.all_siblings:
        projects = sorted(github_dir.glob("azure-*-practical-guide"))
    else:
        projects = [repo_root]

    all_results = {}
    total_errors = 0
    total_redirects = 0
    total_rate_limited = 0

    for project_path in projects:
        if not project_path.is_dir():
            continue

        project_name = project_path.name
        print(f"\n{'=' * 60}")
        print(f"Validating: {project_name}")
        print("=" * 60)

        results = validate_project(project_path, verbose=args.verbose, fix=args.fix)
        all_results[project_name] = results

        if "error" in results:
            print(f"  Error: {results['error']}")
            continue

        print(f"\n  Summary:")
        print(f"    Files checked: {results['files_checked']}")
        print(f"    Unique URLs: {results['total_urls']}")
        print(f"    OK: {len(results['ok'])}")
        print(f"    Redirects: {len(results['redirects'])}")
        print(f"    Errors: {len(results['errors'])}")
        print(f"    Rate limited: {len(results['rate_limited'])}")

        total_errors += len(results["errors"])
        total_redirects += len(results["redirects"])
        total_rate_limited += len(results["rate_limited"])

    # Final summary
    print(f"\n{'=' * 60}")
    print("FINAL SUMMARY")
    print("=" * 60)
    print(f"Projects checked: {len(all_results)}")
    print(f"Total redirects: {total_redirects}")
    print(f"Total errors: {total_errors}")
    print(f"Total rate limited: {total_rate_limited}")

    if total_errors > 0:
        print("\nBroken URLs require manual fixing!")
        sys.exit(1)
    elif total_rate_limited > 0:
        print(
            "\nSome URLs were rate limited after retries; rerun later for full coverage."
        )
        sys.exit(0)
    elif total_redirects > 0:
        print("\nRedirected URLs should be updated to canonical versions.")
        if args.fix:
            print("Run with --fix to auto-update redirected URLs.")
        sys.exit(0)
    else:
        print("\nAll URLs are valid!")
        sys.exit(0)


if __name__ == "__main__":
    main()
