"""SerpAPI Google search collection."""

from __future__ import annotations

from typing import Any

from serpapi import GoogleSearch


SearchResult = dict[str, str]


def search_keyword(
    keyword: str,
    api_key: str,
    *,
    page_size: int,
    page_count: int,
) -> list[SearchResult]:
    """Collect organic Google results for one keyword using start pagination."""
    results: list[SearchResult] = []
    for page_index in range(page_count):
        start = page_index * page_size
        try:
            response: dict[str, Any] = GoogleSearch(
                {
                    "engine": "google",
                    "q": keyword,
                    "api_key": api_key,
                    "start": start,
                    "num": page_size,
                    "hl": "ko",
                    "gl": "kr",
                }
            ).get_dict()
            if "error" in response:
                raise RuntimeError(str(response["error"]))
        except Exception as error:  # SerpAPI errors must not stop other searches.
            print(f"  검색 실패 ({keyword}, start={start}): {error}")
            continue

        for item in response.get("organic_results", []):
            link = item.get("link")
            if not link:
                continue
            results.append(
                {
                    "title": str(item.get("title", "")).strip(),
                    "snippet": str(item.get("snippet", "")).strip(),
                    "url": str(link).strip(),
                }
            )
    return results


def search_all(
    keywords: list[str],
    api_key: str,
    *,
    page_size: int,
    page_count: int,
) -> list[SearchResult]:
    """Collect results for every configured search keyword."""
    all_results: list[SearchResult] = []
    for keyword in keywords:
        print(f"검색 중: {keyword}")
        all_results.extend(
            search_keyword(
                keyword,
                api_key,
                page_size=page_size,
                page_count=page_count,
            )
        )
    return all_results
