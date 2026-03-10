#!/usr/bin/env python3
"""Fetch top forum posts from a community forum.

Usage: python3 fetch-forum-posts.py --community <name> --limit <N> [--api-url <url>]

Output: JSON array of posts to stdout, errors to stderr.
Currently a placeholder — returns an error until forum API is confirmed.
"""

import argparse
import json
import sys


def fetch_posts(community: str, limit: int, api_url: str | None = None) -> list[dict]:
    # TODO: Implement when forum API is confirmed
    # For now, signal that API is unavailable so the skill falls back to LLM generation
    print(
        f"ERROR: Forum API not yet configured for '{community}'. "
        "Falling back to LLM-generated usage questions.",
        file=sys.stderr,
    )
    sys.exit(1)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Fetch forum posts")
    parser.add_argument("--community", required=True)
    parser.add_argument("--limit", type=int, default=50)
    parser.add_argument("--api-url", default=None)
    args = parser.parse_args()

    posts = fetch_posts(args.community, args.limit, args.api_url)
    print(json.dumps(posts, ensure_ascii=False, indent=2))
