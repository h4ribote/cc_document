#!/usr/bin/env python3
"""Mirror the Claude Code documentation pages advertised by llms.txt into a local directory tree.

The root index lists the English pages directly and points at per-language indexes under `_llms/`, of which only the ones named by DEFAULT_INDEXES or `--index` are followed.
"""

from __future__ import annotations

import argparse
import re
import sys
import time
import urllib.error
import urllib.request
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from urllib.parse import urljoin

DOCS_BASE = "https://code.claude.com/docs/"
ROOT_INDEX = "llms.txt"
DEFAULT_INDEXES = ("_llms/jp.md",)
USER_AGENT = "cc_document-sync (+https://github.com/h4ribote/cc_document)"

LINK_PATTERN = re.compile(r"\]\((https://code\.claude\.com/docs/[^)\s]+?\.(?:md|txt))\)")
RETRY_DELAYS = (2, 5, 15)
TEXT_TYPES = ("text/markdown", "text/plain")


class FetchError(RuntimeError):
    """A document could not be retrieved after every retry was exhausted."""


def fetch(url: str) -> tuple[bytes, str]:
    """Return the body and media type of `url`, retrying transient failures before giving up."""
    request = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
    last_error: Exception | None = None
    for attempt in range(len(RETRY_DELAYS) + 1):
        try:
            with urllib.request.urlopen(request, timeout=60) as response:
                return response.read(), response.headers.get_content_type()
        except (urllib.error.URLError, TimeoutError, OSError) as error:
            # A 404 means the index and the site disagree, which no amount of retrying will fix.
            if isinstance(error, urllib.error.HTTPError) and 400 <= error.code < 500:
                raise FetchError(f"{url}: HTTP {error.code}") from error
            last_error = error
            if attempt < len(RETRY_DELAYS):
                time.sleep(RETRY_DELAYS[attempt])
    raise FetchError(f"{url}: {last_error}")


def relative_path(url: str) -> str:
    """Return the path of `url` below the documentation root, e.g. `en/overview.md`."""
    if not url.startswith(DOCS_BASE):
        raise ValueError(f"URL outside the documentation root: {url}")
    return url[len(DOCS_BASE) :]


def linked_pages(body: bytes) -> list[str]:
    """Return the documentation-relative paths linked from an index body, in order and without duplicates."""
    seen: dict[str, None] = {}
    for url in LINK_PATTERN.findall(body.decode("utf-8")):
        seen.setdefault(relative_path(url), None)
    return list(seen)


def collect(indexes: tuple[str, ...]) -> dict[str, bytes]:
    """Fetch the root index plus the requested language indexes and every page they list.

    Returns a mapping of documentation-relative path to file body, covering the index files themselves.
    A listed page the site serves as something other than text, such as a page that resolves to a rendered HTML view, is reported and left out of the mirror.
    """
    documents: dict[str, bytes] = {}
    pending_indexes = [ROOT_INDEX]
    page_paths: dict[str, None] = {}

    while pending_indexes:
        index_path = pending_indexes.pop(0)
        if index_path in documents:
            continue
        print(f"index  {index_path}", flush=True)
        body, media_type = fetch(urljoin(DOCS_BASE, index_path))
        if media_type not in TEXT_TYPES:
            raise FetchError(f"{index_path}: expected text, got {media_type}")
        documents[index_path] = body
        for path in linked_pages(body):
            if path.startswith("_llms/"):
                if path in indexes and path not in documents:
                    pending_indexes.append(path)
            else:
                page_paths.setdefault(path, None)

    def load(path: str) -> tuple[str, bytes | None]:
        body, media_type = fetch(urljoin(DOCS_BASE, path))
        if media_type not in TEXT_TYPES:
            print(f"skip   {path}: {media_type}", flush=True)
            return path, None
        return path, body

    with ThreadPoolExecutor(max_workers=8) as pool:
        for path, body in pool.map(load, page_paths):
            if body is not None:
                documents[path] = body
    print(f"fetched {len(documents)} files", flush=True)
    return documents


def write_tree(destination: Path, documents: dict[str, bytes]) -> tuple[int, int, int]:
    """Write `documents` under `destination`, delete files no longer listed, and return the added, updated and removed counts."""
    added = updated = 0
    for path, body in sorted(documents.items()):
        target = destination / path
        target.parent.mkdir(parents=True, exist_ok=True)
        if not target.exists():
            added += 1
        elif target.read_bytes() != body:
            updated += 1
        else:
            continue
        target.write_bytes(body)

    expected = {(destination / path).resolve() for path in documents}
    removed = 0
    for existing in sorted(destination.rglob("*")):
        if existing.is_file() and existing.resolve() not in expected:
            existing.unlink()
            removed += 1
    for directory in sorted(destination.rglob("*"), reverse=True):
        if directory.is_dir() and not any(directory.iterdir()):
            directory.rmdir()
    return added, updated, removed


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--dest", type=Path, default=Path(__file__).resolve().parent.parent / "docs", help="directory the mirror is written to")
    parser.add_argument("--index", action="append", default=None, metavar="PATH", help=f"language index to follow, relative to {DOCS_BASE} (default: {', '.join(DEFAULT_INDEXES)})")
    arguments = parser.parse_args(argv)

    indexes = tuple(arguments.index) if arguments.index is not None else DEFAULT_INDEXES
    try:
        documents = collect(indexes)
    except (FetchError, ValueError) as error:
        # Aborting before any write keeps a transient network failure from pruning the mirror.
        print(f"error: {error}", file=sys.stderr)
        return 1

    added, updated, removed = write_tree(arguments.dest, documents)
    print(f"added {added}, updated {updated}, removed {removed}", flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
