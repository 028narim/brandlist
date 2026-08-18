"""Google Sheets persistence using a service account."""

from __future__ import annotations

import gspread
from google.oauth2.service_account import Credentials


SCOPES = ["https://www.googleapis.com/auth/spreadsheets"]
HEADER = ["브랜드명(판매사이트)", "사이트 링크", "이메일"]


def append_to_sheet(
    records: list[dict[str, str]],
    *,
    credentials_path: str,
    spreadsheet_id: str,
) -> int:
    """Append records to the first worksheet, adding a header when it is empty."""
    credentials = Credentials.from_service_account_file(credentials_path, scopes=SCOPES)
    client = gspread.authorize(credentials)
    worksheet = client.open_by_key(spreadsheet_id).get_worksheet(0)
    if worksheet is None:
        raise RuntimeError("첫 번째 워크시트를 찾을 수 없습니다.")

    if not worksheet.row_values(1):
        worksheet.append_row(HEADER, value_input_option="RAW")

    rows = [[record["brand_name"], record["url"], record["email"]] for record in records]
    if rows:
        worksheet.append_rows(rows, value_input_option="RAW")
    return len(rows)
