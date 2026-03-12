#!/usr/bin/env python3
"""Compile improvement report from diagnostics, patterns, and suggestions.

Reads JSON from stdin, deduplicates suggestions, sorts by priority, assigns IDs,
and outputs the final improvement-report.json to stdout.
"""

import json
import sys
from difflib import SequenceMatcher


def similarity(a: str, b: str) -> float:
    """Compute text similarity ratio between two strings."""
    return SequenceMatcher(None, a.lower(), b.lower()).ratio()


def deduplicate_suggestions(suggestions: list, threshold: float = 0.8) -> list:
    """Remove suggestions with >threshold text similarity in recommended_change."""
    if not suggestions:
        return []

    unique = [suggestions[0]]
    for s in suggestions[1:]:
        s_text = s.get("recommended_change", "") + s.get("title", "")
        is_dup = False
        for u in unique:
            u_text = u.get("recommended_change", "") + u.get("title", "")
            if similarity(s_text, u_text) > threshold:
                # Keep the higher priority one
                priority_order = {"P0": 0, "P1": 1, "P2": 2}
                s_pri = priority_order.get(s.get("priority", "P2"), 2)
                u_pri = priority_order.get(u.get("priority", "P2"), 2)
                if s_pri < u_pri:
                    unique.remove(u)
                    unique.append(s)
                is_dup = True
                break
        if not is_dup:
            unique.append(s)
    return unique


def assign_ids(suggestions: list, prefix: str) -> list:
    """Assign unique IDs to suggestions."""
    for i, s in enumerate(suggestions, 1):
        s["id"] = f"{prefix}-{i:03d}"
    return suggestions


def sort_by_priority(suggestions: list) -> list:
    """Sort suggestions by priority (P0 first) then by category."""
    priority_order = {"P0": 0, "P1": 1, "P2": 2}
    return sorted(suggestions, key=lambda s: (
        priority_order.get(s.get("priority", "P2"), 2),
        s.get("category", s.get("dimension", "zzz"))
    ))


def main():
    try:
        data = json.load(sys.stdin)
    except json.JSONDecodeError as e:
        print(f"ERROR: Invalid JSON input: {e}", file=sys.stderr)
        sys.exit(1)

    diagnostics = data.get("diagnostics", [])
    patterns = data.get("patterns", {})
    question_suggestions = data.get("question_suggestions", [])
    universal_suggestions = data.get("universal_suggestions", [])
    metadata = data.get("metadata", {})

    # Deduplicate
    question_suggestions = deduplicate_suggestions(question_suggestions)
    universal_suggestions = deduplicate_suggestions(universal_suggestions)

    # Sort
    question_suggestions = sort_by_priority(question_suggestions)
    universal_suggestions = sort_by_priority(universal_suggestions)

    # Assign IDs
    question_suggestions = assign_ids(question_suggestions, "QS")
    universal_suggestions = assign_ids(universal_suggestions, "US")

    # Compute summary stats
    def count_by_priority(items):
        counts = {"P0": 0, "P1": 0, "P2": 0}
        for item in items:
            p = item.get("priority", "P2")
            counts[p] = counts.get(p, 0) + 1
        return counts

    failure_modes = set()
    severity_dist = {"none": 0, "low": 0, "medium": 0, "high": 0, "critical": 0}
    for d in diagnostics:
        mode = d.get("failure_mode", "none")
        if mode != "none":
            failure_modes.add(mode)
        sev = d.get("severity", "none")
        severity_dist[sev] = severity_dist.get(sev, 0) + 1

    report = {
        "metadata": metadata,
        "summary": {
            "total_diagnostics": len(diagnostics),
            "failure_modes_found": sorted(failure_modes),
            "severity_distribution": severity_dist,
            "question_suggestions_count": len(question_suggestions),
            "question_suggestions_by_priority": count_by_priority(question_suggestions),
            "universal_suggestions_count": len(universal_suggestions),
            "universal_suggestions_by_priority": count_by_priority(universal_suggestions),
        },
        "diagnostics": diagnostics,
        "patterns": patterns,
        "question_suggestions": question_suggestions,
        "universal_suggestions": universal_suggestions,
    }

    json.dump(report, sys.stdout, ensure_ascii=False, indent=2)
    print(f"\nCompiled: {len(question_suggestions)} per-question + {len(universal_suggestions)} universal suggestions",
          file=sys.stderr)


if __name__ == "__main__":
    main()
