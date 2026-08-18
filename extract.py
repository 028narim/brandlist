"""Retailer name and email extraction from a candidate website."""

from __future__ import annotations

import re
from urllib.parse import unquote

import requests
from bs4 import BeautifulSoup, Tag


EMAIL_PATTERN = re.compile(r"[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}", re.IGNORECASE)
HEADERS = {"User-Agent": "Mozilla/5.0 (compatible; BrandlistBot/1.0)"}


def _footer_nodes(soup: BeautifulSoup) -> list[Tag]:
    nodes = list(soup.find_all("footer"))
    nodes.extend(
        tag
        for tag in soup.find_all(True)
        if tag not in nodes
        and any("footer" in str(value).lower() for value in (tag.get("id"), tag.get("class")))
    )
    return nodes


def _mailto_email(node: BeautifulSoup | Tag) -> str | None:
    link = node.find("a", href=re.compile(r"^mailto:", re.IGNORECASE))
    if not link:
        return None
    href = str(link.get("href", ""))
    email = unquote(href.split(":", 1)[1].split("?", 1)[0]).strip()
    return email if EMAIL_PATTERN.fullmatch(email) else None


def _regex_email(text: str) -> str | None:
    match = EMAIL_PATTERN.search(text)
    return match.group(0) if match else None


def extract_email(soup: BeautifulSoup) -> str:
    """Find an email, prioritizing footer content and mailto links."""
    footers = _footer_nodes(soup)
    for footer in footers:
        if email := _mailto_email(footer):
            return email
    if email := _mailto_email(soup):
        return email
    for footer in footers:
        if email := _regex_email(footer.get_text(" ", strip=True)):
            return email
    return _regex_email(soup.get_text(" ", strip=True)) or "없음"


def extract_site_info(result: dict[str, str], timeout: int) -> dict[str, str]:
    """Fetch a site and extract its title and email with a safe fallback."""
    fallback = {"brand_name": result.get("title", ""), "url": result["url"], "email": "없음"}
    try:
        response = requests.get(result["url"], headers=HEADERS, timeout=timeout)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, "html.parser")
        title = soup.title.get_text(" ", strip=True) if soup.title else ""
        return {
            "brand_name": title or fallback["brand_name"],
            "url": result["url"],
            "email": extract_email(soup),
        }
    except (requests.RequestException, ValueError) as error:
        print(f"  사이트 접속 실패 ({result['url']}): {error}")
        return fallback
