"""Result filtering for fishing-tackle retailer candidates."""

from __future__ import annotations

from urllib.parse import urlparse


FISHING_KEYWORDS = ("낚시", "fishing", "tackle", "낚싯대", "루어")
EXCLUDED_DOMAIN_SUFFIXES = (
    "naver.com",
    "coupang.com",
    "gmarket.co.kr",
    "11st.co.kr",
    "auction.co.kr",
    "interpark.com",
    "wemakeprice.com",
    "tmon.co.kr",
    "ssg.com",
    "blogspot.com",
    "tistory.com",
    "brunch.co.kr",
    "instagram.com",
    "youtube.com",
    "youtu.be",
    "facebook.com",
    "x.com",
    "twitter.com",
    "kakao.com",
    "daum.net",
)


def normalized_host(url: str) -> str:
    """Return a lowercase hostname without a leading www."""
    host = (urlparse(url).hostname or "").lower()
    return host.removeprefix("www.")


def is_excluded_domain(url: str) -> bool:
    host = normalized_host(url)
    return any(host == suffix or host.endswith(f".{suffix}") for suffix in EXCLUDED_DOMAIN_SUFFIXES)


def has_fishing_keyword(result: dict[str, str]) -> bool:
    text = f"{result.get('title', '')} {result.get('snippet', '')}".lower()
    return any(keyword in text for keyword in FISHING_KEYWORDS)


def filter_results(results: list[dict[str, str]]) -> list[dict[str, str]]:
    """Keep only fishing-relevant, non-platform web results."""
    return [
        result
        for result in results
        if normalized_host(result.get("url", ""))
        and not is_excluded_domain(result["url"])
        and has_fishing_keyword(result)
    ]
