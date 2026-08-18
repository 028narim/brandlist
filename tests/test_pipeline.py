from __future__ import annotations

import unittest
from unittest.mock import Mock, patch

from bs4 import BeautifulSoup

from dedupe import deduplicate_by_domain
from extract import extract_email, extract_site_info
from filter import filter_results
from sheets import HEADER, append_to_sheet, get_existing_domains


class FilterAndDedupeTests(unittest.TestCase):
    def test_filters_platform_and_non_fishing_results(self) -> None:
        results = [
            {"title": "낚시용품 전문몰", "snippet": "루어와 낚싯대", "url": "https://shop.example.kr"},
            {"title": "낚시용품", "snippet": "판매", "url": "https://www.coupang.com/item"},
            {"title": "일반 쇼핑몰", "snippet": "생활용품", "url": "https://other.example.kr"},
        ]
        self.assertEqual(filter_results(results), [results[0]])

    def test_deduplicates_www_domain(self) -> None:
        results = [
            {"url": "https://www.example.kr/a"},
            {"url": "https://example.kr/b"},
            {"url": "https://another.example.kr"},
        ]
        self.assertEqual(deduplicate_by_domain(results), [results[0], results[2]])


class ExtractionTests(unittest.TestCase):
    def test_footer_mailto_has_priority(self) -> None:
        soup = BeautifulSoup(
            '<a href="mailto:body@example.com">body</a><footer><a href="mailto:footer@example.com">footer</a></footer>',
            "html.parser",
        )
        self.assertEqual(extract_email(soup), "footer@example.com")

    def test_text_email_and_missing_email(self) -> None:
        self.assertEqual(
            extract_email(BeautifulSoup("<footer>문의 fish@example.com</footer>", "html.parser")),
            "fish@example.com",
        )
        self.assertEqual(extract_email(BeautifulSoup("<p>no contact</p>", "html.parser")), "없음")

    @patch("extract.requests.get")
    def test_request_failure_uses_search_result_fallback(self, get: Mock) -> None:
        get.side_effect = __import__("requests").RequestException("offline")
        result = {"title": "검색 제목", "url": "https://example.kr"}
        self.assertEqual(
            extract_site_info(result, 8),
            {"brand_name": "검색 제목", "url": "https://example.kr", "email": "없음"},
        )


class SheetTests(unittest.TestCase):
    @patch("sheets.gspread.authorize")
    @patch("sheets.Credentials.from_service_account_file")
    def test_reads_existing_domains_from_site_link_column(self, credentials: Mock, authorize: Mock) -> None:
        worksheet = Mock()
        worksheet.col_values.return_value = [HEADER[1], "https://www.example.kr", "not a url"]
        authorize.return_value.open_by_key.return_value.get_worksheet.return_value = worksheet

        domains = get_existing_domains(credentials_path="credentials.json", spreadsheet_id="sheet-id")

        self.assertEqual(domains, {"example.kr"})

    @patch("sheets.gspread.authorize")
    @patch("sheets.Credentials.from_service_account_file")
    def test_adds_header_to_empty_sheet_and_appends_rows(self, credentials: Mock, authorize: Mock) -> None:
        worksheet = Mock()
        worksheet.row_values.return_value = []
        authorize.return_value.open_by_key.return_value.get_worksheet.return_value = worksheet
        records = [{"brand_name": "낚시몰", "url": "https://example.kr", "email": "fish@example.kr"}]

        saved = append_to_sheet(records, credentials_path="credentials.json", spreadsheet_id="sheet-id")

        self.assertEqual(saved, 1)
        worksheet.append_row.assert_called_once_with(HEADER, value_input_option="RAW")
        worksheet.append_rows.assert_called_once_with(
            [["낚시몰", "https://example.kr", "fish@example.kr"]], value_input_option="RAW"
        )


if __name__ == "__main__":
    unittest.main()
