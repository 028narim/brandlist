"""Application configuration loaded from the local .env file."""

from __future__ import annotations

import os
from pathlib import Path

from dotenv import load_dotenv


SEARCH_KEYWORDS = [
    "낚시용품 쇼핑몰",
    "낚시용품 인터넷쇼핑몰",
    "낚시 전문 쇼핑몰",
    "낚싯대 판매 사이트",
    "낚시용품 온라인 스토어",
    "fishing tackle online shop",
    "fishing gear store site:.co.kr",
]
SEARCH_PAGE_SIZE = 10
SEARCH_PAGES_PER_KEYWORD = 5
TARGET_SITE_COUNT = 100
REQUEST_TIMEOUT_SECONDS = 8


class ConfigError(ValueError):
    """Raised when required local configuration is missing."""


def load_config() -> dict[str, str]:
    """Load and validate required credentials from .env and the environment."""
    load_dotenv()
    values = {
        "serpapi_key": os.getenv("SERPAPI_KEY", "").strip(),
        "credentials_path": os.getenv("GOOGLE_SHEETS_CREDENTIALS_PATH", "").strip(),
        "spreadsheet_id": os.getenv("SPREADSHEET_ID", "").strip(),
    }
    missing = [name for name, value in values.items() if not value]
    if missing:
        names = {
            "serpapi_key": "SERPAPI_KEY",
            "credentials_path": "GOOGLE_SHEETS_CREDENTIALS_PATH",
            "spreadsheet_id": "SPREADSHEET_ID",
        }
        raise ConfigError(f".env 필수 값이 비어 있습니다: {', '.join(names[name] for name in missing)}")

    credentials_path = Path(values["credentials_path"])
    if not credentials_path.is_file():
        raise ConfigError(f"서비스 계정 파일을 찾을 수 없습니다: {credentials_path}")
    return values
