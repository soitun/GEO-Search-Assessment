#!/usr/bin/env python3
"""Create a GitCode Issue from a JSON payload.

Usage:
    python3 create-issue.py --owner <owner> --repo <repo> --payload '<json>' [--dry-run]

In normal mode, POSTs to GitCode API and prints the created Issue URL.
In dry-run mode, prints the payload to stdout without calling the API.

Requires GITCODE_TOKEN environment variable (or --token flag).
"""

import argparse
import json
import os
import sys
import urllib.error
import urllib.request


API_BASE = "https://api.gitcode.com/api/v5"


def create_issue(owner, repo, payload, token, dry_run=False):
    """Create a single Issue on GitCode."""
    try:
        issue_data = json.loads(payload)
    except json.JSONDecodeError as e:
        print(f"ERROR: Invalid JSON payload: {e}", file=sys.stderr)
        sys.exit(1)

    title = issue_data.get("title", "")
    body = issue_data.get("body", "")
    labels = issue_data.get("labels", "")

    if not title:
        print("ERROR: Issue title is required", file=sys.stderr)
        sys.exit(1)

    if dry_run:
        output = {
            "mode": "dry-run",
            "owner": owner,
            "repo": repo,
            "title": title,
            "labels": labels,
            "body": body[:200] + "..." if len(body) > 200 else body,
        }
        json.dump(output, sys.stdout, ensure_ascii=False, indent=2)
        print()
        return

    # Build request
    url = f"{API_BASE}/repos/{owner}/{repo}/issues"
    request_body = json.dumps({
        "access_token": token,
        "repo": repo,
        "title": title,
        "body": body,
        "labels": labels,
    }).encode("utf-8")

    req = urllib.request.Request(
        url,
        data=request_body,
        headers={
            "Content-Type": "application/json",
            "private-token": token,
        },
        method="POST",
    )

    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            result = json.loads(resp.read().decode("utf-8"))
            issue_url = result.get("html_url", f"https://gitcode.com/{owner}/{repo}/issues/{result.get('number', '?')}")
            print(json.dumps({
                "status": "created",
                "url": issue_url,
                "number": result.get("number", ""),
                "title": title,
            }, ensure_ascii=False))
    except urllib.error.HTTPError as e:
        error_body = e.read().decode("utf-8", errors="replace") if e.fp else ""
        print(f"ERROR: HTTP {e.code} creating issue: {error_body}", file=sys.stderr)
        if e.code == 403:
            print("HINT: Check that GITCODE_TOKEN has 'write_issues' scope.", file=sys.stderr)
        sys.exit(1)
    except urllib.error.URLError as e:
        print(f"ERROR: Network error: {e.reason}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Create a GitCode Issue")
    parser.add_argument("--owner", required=True, help="Repository owner")
    parser.add_argument("--repo", required=True, help="Repository name")
    parser.add_argument("--payload", required=True, help="JSON payload with title, body, labels")
    parser.add_argument("--token", default=None, help="GitCode API token (overrides env)")
    parser.add_argument("--dry-run", action="store_true", help="Print payload without calling API")
    args = parser.parse_args()

    token = args.token or os.environ.get("GITCODE_TOKEN", "")
    if not token and not args.dry_run:
        print("ERROR: GITCODE_TOKEN not set. Cannot create Issues.", file=sys.stderr)
        sys.exit(1)

    create_issue(args.owner, args.repo, args.payload, token, args.dry_run)
