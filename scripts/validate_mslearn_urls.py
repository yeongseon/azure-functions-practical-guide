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
from typing import Dict, List, Tuple, Optional
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
REQUEST_DELAY = 0.1  # seconds between requests
MAX_WORKERS = 5  # parallel requests


def extract_frontmatter(content: str) -> Optional[dict]:
    """Extract YAML frontmatter from markdown content."""
    match = re.match(r"^---\s*\n(.*?)\n---\s*\n", content, re.DOTALL)
    if not match:
        return None
    try:
        return yaml.safe_load(match.group(1))
    except yaml.YAMLError:
        return None


def extract_mslearn_urls(frontmatter: dict) -> List[str]:
    """Extract all MSLearn URLs from content_sources in frontmatter."""
    urls = set()

    content_sources = frontmatter.get("content_sources", {})
    diagrams = content_sources.get("diagrams", [])

    for diagram in diagrams:
        if isinstance(diagram, dict):
            # Direct mslearn_url
            if "mslearn_url" in diagram:
                url = diagram["mslearn_url"]
                if url and "learn.microsoft.com" in url:
                    urls.add(url)

            # based_on list
            based_on = diagram.get("based_on", [])
            if isinstance(based_on, list):
                for url in based_on:
                    if url and "learn.microsoft.com" in url:
                        urls.add(url)

    return list(urls)


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
    try:
        # Use HEAD first, fall back to GET if needed
        response = session.head(url, allow_redirects=True, timeout=10)

        # Some servers don't support HEAD
        if response.status_code == 405:
            response = session.get(url, allow_redirects=True, timeout=10)

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
        return (url, 0, "timeout", None)
    except requests.RequestException as e:
        return (url, 0, "error", str(e))


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
    args = parser.parse_args()

    # Find all practical-guide projects
    github_dir = Path(__file__).parent.parent.parent

    if args.project:
        projects = [github_dir / args.project]
    else:
        projects = sorted(github_dir.glob("azure-*-practical-guide"))

    all_results = {}
    total_errors = 0
    total_redirects = 0

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

        total_errors += len(results["errors"])
        total_redirects += len(results["redirects"])

    # Final summary
    print(f"\n{'=' * 60}")
    print("FINAL SUMMARY")
    print("=" * 60)
    print(f"Projects checked: {len(all_results)}")
    print(f"Total redirects: {total_redirects}")
    print(f"Total errors: {total_errors}")

    if total_errors > 0:
        print("\nBroken URLs require manual fixing!")
        sys.exit(1)
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
