"""
구글 시트에 자동화 템플릿을 생성하는 스크립트
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
기존 빈 구글 시트에 접수데이터/설정/사용법 시트를 자동으로 세팅합니다.

사용법:
  python setup_sheet.py --url "https://docs.google.com/spreadsheets/d/..."
"""

import argparse
import sys
from pathlib import Path

try:
    import gspread
    from google.oauth2.service_account import Credentials
except ImportError:
    print("❌ gspread가 설치되지 않았습니다:")
    print("   pip install gspread google-auth")
    sys.exit(1)

SERVICE_ACCOUNT_FILE = "service_account.json"
SCOPES = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive",
]


def setup_sheet(spreadsheet_url: str):
    if not Path(SERVICE_ACCOUNT_FILE).exists():
        print(f"❌ {SERVICE_ACCOUNT_FILE} 파일이 없습니다.")
        print("   Google Cloud Console에서 서비스 계정 키를 다운로드하세요.")
        sys.exit(1)

    creds = Credentials.from_service_account_file(SERVICE_ACCOUNT_FILE, scopes=SCOPES)
    gc = gspread.authorize(creds)
    sh = gc.open_by_url(spreadsheet_url)

    print(f"📊 스프레드시트: {sh.title}")

    # ── Sheet 1: 접수데이터 ──
    print("  [1/3] 접수데이터 시트 생성...")
    try:
        ws1 = sh.worksheet("접수데이터")
        ws1.clear()
    except gspread.exceptions.WorksheetNotFound:
        ws1 = sh.add_worksheet(title="접수데이터", rows=110, cols=10)

    # 헤더
    ws1.update("A1", [["🔄 쿠팡이츠 리뷰 블라인드/게시중단 자동 접수 시트"]])
    ws1.merge_cells("A1:I1")
    ws1.update("A2", [["※ 파란색 영역에 데이터를 입력하세요. H~I열은 자동화 실행 시 자동 기록됩니다."]])
    ws1.merge_cells("A2:I2")

    headers = [["No.", "스토어 ID\n(6자리)", "사업자등록번호\n(000-00-00000)",
                "주문번호", "주문일자\n(YYYY-MM-DD)", "신청사유\n(상세 기술)",
                "신청유형", "처리결과", "처리시간"]]
    ws1.update("A3", headers)

    # 샘플 데이터
    samples = [
        [1, "123456", "123-45-67890", "ORD-2025-0001", "2025-02-15",
         "허위 리뷰 - 실제 주문과 무관한 내용 작성", "블라인드&게시중단 중복", "", ""],
        [2, "789012", "987-65-43210", "ORD-2025-0002", "2025-02-16",
         "비방/욕설 포함 - 음식과 무관한 인신공격", "블라인드&게시중단 중복", "", ""],
        [3, "345678", "111-22-33333", "ORD-2025-0003", "2025-02-17",
         "경쟁업체 의심 - 동일 시간대 유사 패턴", "블라인드&게시중단 중복", "", ""],
    ]
    ws1.update("A4", samples)

    # 번호 채우기 (4~103)
    numbers = [[i] for i in range(4, 101)]
    ws1.update("A7", numbers)

    # 드롭다운 (G열 - 신청유형)
    ws1.set_basic_filter("A3:I103")

    # 서식
    ws1.format("A1:I1", {"textFormat": {"bold": True, "fontSize": 14}})
    ws1.format("A3:I3", {
        "backgroundColor": {"red": 0.18, "green": 0.46, "blue": 0.71},
        "textFormat": {"bold": True, "foregroundColor": {"red": 1, "green": 1, "blue": 1}, "fontSize": 10},
        "horizontalAlignment": "CENTER",
        "wrapStrategy": "WRAP",
    })
    ws1.format("B4:F103", {
        "backgroundColor": {"red": 1, "green": 0.95, "blue": 0.8},
        "textFormat": {"foregroundColor": {"red": 0, "green": 0, "blue": 1}},
    })

    # 열 너비
    sheet_id = ws1.id
    requests = []
    widths = [50, 120, 170, 150, 120, 300, 150, 120, 160]
    for i, w in enumerate(widths):
        requests.append({
            "updateDimensionProperties": {
                "range": {"sheetId": sheet_id, "dimension": "COLUMNS", "startIndex": i, "endIndex": i+1},
                "properties": {"pixelSize": w},
                "fields": "pixelSize",
            }
        })
    sh.batch_update({"requests": requests})

    # ── Sheet 2: 설정 ──
    print("  [2/3] 설정 시트 생성...")
    try:
        ws2 = sh.worksheet("설정")
        ws2.clear()
    except gspread.exceptions.WorksheetNotFound:
        ws2 = sh.add_worksheet(title="설정", rows=20, cols=4)

    ws2.update("A1", [["⚙️ 자동화 설정"]])
    ws2.merge_cells("A1:C1")
    ws2.update("A3", [["설정 항목", "값", "설명"]])
    settings = [
        ["챗봇 URL", "https://buly.kr/BpEMAeD", "쿠팡이츠 Happytalk 챗봇 URL"],
        ["건당 대기시간(초)", "3", "각 접수 건 사이 대기 시간"],
        ["요소 탐지 타임아웃(초)", "10", "챗봇 버튼/메시지 대기 최대 시간"],
        ["최대 재시도 횟수", "3", "실패 시 재시도 횟수"],
        ["브라우저 표시", "TRUE", "TRUE=브라우저 보임, FALSE=백그라운드"],
        ["스크린샷 저장", "TRUE", "에러 발생 시 스크린샷 저장"],
        ["사유 카테고리", "기타", "기타 / 허위리뷰 / 비방 등"],
        ["댓글 삭제 동의", "네", "네 / 아니오"],
    ]
    ws2.update("A4", settings)

    ws2.format("A1:C1", {"textFormat": {"bold": True, "fontSize": 14}})
    ws2.format("A3:C3", {
        "backgroundColor": {"red": 0.18, "green": 0.46, "blue": 0.71},
        "textFormat": {"bold": True, "foregroundColor": {"red": 1, "green": 1, "blue": 1}},
    })
    ws2.format("B4:B11", {
        "backgroundColor": {"red": 1, "green": 0.95, "blue": 0.8},
        "textFormat": {"foregroundColor": {"red": 0, "green": 0, "blue": 1}},
    })

    # ── Sheet 3: 사용법 ──
    print("  [3/3] 사용법 시트 생성...")
    try:
        ws3 = sh.worksheet("사용법")
        ws3.clear()
    except gspread.exceptions.WorksheetNotFound:
        ws3 = sh.add_worksheet(title="사용법", rows=20, cols=3)

    ws3.update("A1", [["📖 사용 방법 안내"]])
    ws3.merge_cells("A1:B1")
    guide = [
        ["Step 1", "서버 실행: python server.py (터미널에서 1회만 실행)"],
        ["Step 2", "브라우저에서 http://localhost:8000 접속"],
        ["Step 3", "이 구글 시트 URL을 대시보드에 붙여넣기 → 연결"],
        ["Step 4", "접수데이터 시트에 리뷰 정보 입력"],
        ["Step 5", "대시보드에서 '자동화 시작' 클릭"],
        ["Step 6", "실행 완료 후 H~I열에 결과 자동 기록"],
        ["주의", "1건씩 순차 처리, 건당 약 1~2분 소요. 실행 중 시트 수정 금지."],
    ]
    ws3.update("A3", guide)
    ws3.format("A1:B1", {"textFormat": {"bold": True, "fontSize": 14}})

    # 기본 시트(Sheet1) 삭제 시도
    try:
        default = sh.worksheet("Sheet1")
        sh.del_worksheet(default)
    except Exception:
        pass
    try:
        default = sh.worksheet("시트1")
        sh.del_worksheet(default)
    except Exception:
        pass

    print(f"\n✅ 템플릿 설정 완료!")
    print(f"   URL: {spreadsheet_url}")
    print(f"   시트: 접수데이터, 설정, 사용법")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="구글 시트에 자동화 템플릿 생성")
    parser.add_argument("--url", required=True, help="Google Sheets URL")
    args = parser.parse_args()
    setup_sheet(args.url)
