"""Domain-based candidate deduplication."""

from __future__ import annotations

from filter import normalized_host


def deduplicate_by_domain(results: list[dict[str, str]]) -> list[dict[str, str]]:
    """Keep the first result for each normalized hostname."""
    seen_domains: set[str] = set()
    unique_results: list[dict[str, str]] = []
    for result in results:
        domain = normalized_host(result.get("url", ""))
        if not domain or domain in seen_domains:
            continue
        seen_domains.add(domain)
        unique_results.append(result)
    return unique_results
