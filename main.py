"""Run the fishing-tackle retailer discovery pipeline once."""

from __future__ import annotations

from config import (
    ConfigError,
    REQUEST_TIMEOUT_SECONDS,
    SEARCH_KEYWORDS,
    SEARCH_PAGE_SIZE,
    SEARCH_PAGES_PER_KEYWORD,
    TARGET_SITE_COUNT,
    load_config,
)
from dedupe import deduplicate_by_domain
from extract import extract_site_info
from filter import filter_results, normalized_host
from search import search_all
from sheets import append_to_sheet, get_existing_domains


def main() -> int:
    try:
        config = load_config()
    except ConfigError as error:
        print(f"설정 오류: {error}")
        return 1

    try:
        existing_domains = get_existing_domains(
            credentials_path=config["credentials_path"],
            spreadsheet_id=config["spreadsheet_id"],
        )
    except Exception as error:
        print(f"Google Sheets 기존 데이터 확인 실패: {error}")
        return 1

    remaining_count = max(TARGET_SITE_COUNT - len(existing_domains), 0)
    print(f"시트 기존 도메인: {len(existing_domains)}개 / 목표: {TARGET_SITE_COUNT}개")
    if remaining_count == 0:
        print("목표 수량에 도달해 추가 수집을 건너뜁니다.")
        return 0

    print("낚시용품 판매처 수집을 시작합니다.")
    search_results = search_all(
        SEARCH_KEYWORDS,
        config["serpapi_key"],
        page_size=SEARCH_PAGE_SIZE,
        page_count=SEARCH_PAGES_PER_KEYWORD,
    )
    print(f"검색 결과: {len(search_results)}개")

    filtered_results = filter_results(search_results)
    print(f"필터 통과: {len(filtered_results)}개")

    unique_results = deduplicate_by_domain(filtered_results)
    print(f"도메인 중복 제거 후: {len(unique_results)}개")

    new_results = [
        result for result in unique_results if normalized_host(result["url"]) not in existing_domains
    ][:remaining_count]
    print(f"시트 기존 도메인 제외 후: {len(new_results)}개")

    extracted = [extract_site_info(result, REQUEST_TIMEOUT_SECONDS) for result in new_results]
    print(f"정보 추출 완료: {len(extracted)}개")

    try:
        saved_count = append_to_sheet(
            extracted,
            credentials_path=config["credentials_path"],
            spreadsheet_id=config["spreadsheet_id"],
        )
    except Exception as error:
        print(f"Google Sheets 저장 실패: {error}")
        return 1

    print(f"Google Sheets 저장 완료: {saved_count}개")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
