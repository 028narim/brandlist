# Brandlist

낚시용품을 판매하는 자체 쇼핑몰을 검색해 Google Sheets에 저장하는 로컬 Python CLI입니다.
상품 브랜드나 대형 오픈마켓은 수집 대상에서 제외합니다.

## 준비물

1. [SerpAPI](https://serpapi.com/)에서 API 키를 발급받습니다.
2. Google Cloud Console에서 서비스 계정을 만들고 JSON 키를 다운로드해 프로젝트 루트에
   `credentials.json`으로 저장합니다.
3. 저장할 Google Sheets를 서비스 계정 이메일에 **편집자** 권한으로 공유합니다.
4. `.env.example`을 복사해 `.env`를 만들고 값을 입력합니다.

   ```bash
   cp .env.example .env
   ```

## 실행

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python main.py
```

검색 결과는 낚시 관련 키워드를 포함하고 제외 도메인에 속하지 않는 사이트만 대상으로 합니다.
사이트 접속에 실패한 경우에도 검색 결과 제목과 `없음` 이메일로 기록하며 다음 항목을 계속 처리합니다.

## 테스트

```bash
python -m unittest discover -s tests
```
