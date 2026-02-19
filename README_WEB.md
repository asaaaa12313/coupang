# 🔄 쿠팡이츠 리뷰 게시중단 자동화 (웹 대시보드 버전)

웹 브라우저에서 Google Sheets와 연동하여 쿠팡이츠 리뷰 게시중단을 자동 접수하는 시스템입니다.

---

## 📁 파일 구조

```
coupang-review-web/
├── server.py              # FastAPI 백엔드 서버
├── setup_sheet.py         # 구글 시트 템플릿 생성 스크립트
├── static/
│   └── index.html         # 웹 대시보드 UI
├── service_account.json   # (직접 생성) 구글 서비스 계정 키
├── requirements_web.txt   # 의존성 패키지
├── screenshots/           # (자동 생성) 에러 스크린샷
└── README_WEB.md          # 이 문서
```

---

## 🚀 설치 & 실행 (총 5단계)

### Step 1: 패키지 설치

```bash
pip install -r requirements_web.txt
playwright install chromium
```

### Step 2: Google Cloud 서비스 계정 설정

1. [Google Cloud Console](https://console.cloud.google.com/) 접속
2. 프로젝트 생성 (또는 기존 프로젝트 선택)
3. **API 활성화**:
   - `Google Sheets API` 검색 → 사용 설정
   - `Google Drive API` 검색 → 사용 설정
4. **서비스 계정 생성**:
   - 좌측 메뉴 → IAM 및 관리자 → 서비스 계정
   - "서비스 계정 만들기" 클릭
   - 이름 입력 (예: coupang-automation) → 만들기
   - 역할: 건너뛰기 (불필요)
   - 완료
5. **키 생성**:
   - 생성된 서비스 계정 클릭 → 키 탭
   - "키 추가" → "새 키 만들기" → JSON → 만들기
   - 다운로드된 파일을 `service_account.json`으로 이름 변경
   - `server.py`와 같은 폴더에 저장

### Step 3: Google Sheets 준비

1. [Google Sheets](https://sheets.google.com)에서 **새 스프레드시트** 생성
2. 서비스 계정에 **편집 권한** 부여:
   - 스프레드시트 우측 상단 "공유" 클릭
   - `service_account.json` 안의 `client_email` 주소 입력
   - "편집자" 권한으로 공유
3. 템플릿 자동 생성:

```bash
python setup_sheet.py --url "https://docs.google.com/spreadsheets/d/여기에_시트_ID/edit"
```

> 이 스크립트가 접수데이터, 설정, 사용법 3개 시트를 자동으로 세팅합니다.

### Step 4: 서버 실행

```bash
python server.py
```

서버가 `http://localhost:8000`에서 실행됩니다.

### Step 5: 대시보드 접속 & 사용

1. 브라우저에서 **http://localhost:8000** 접속
2. Google Sheets URL 붙여넣기 → **연결** 클릭
3. 데이터 확인 후 → **▶ 자동화 시작** 클릭
4. 실시간 로그와 진행상황을 대시보드에서 확인
5. 완료 후 Google Sheets H~I열에 결과 자동 기록

---

## 💡 사용 흐름

```
┌─────────────┐     ┌──────────────┐     ┌───────────────┐
│ Google Sheets │ ←→ │  서버 (8000)  │ ←→ │  웹 대시보드    │
│  (데이터)     │     │  FastAPI     │     │  (브라우저)     │
│              │     │  + Playwright │     │               │
└─────────────┘     └──────────────┘     └───────────────┘

1. 담당자가 구글 시트에 접수 데이터 입력
2. 대시보드에서 시트 연결 → 데이터 확인
3. "자동화 시작" 클릭
4. 서버가 Playwright로 챗봇 자동 접수
5. 결과가 실시간으로 대시보드에 표시 + 시트에 기록
```

---

## ⚙️ 설정 항목 (구글 시트 [설정] 탭)

| 항목 | 기본값 | 설명 |
|------|--------|------|
| 챗봇 URL | https://buly.kr/BpEMAeD | 쿠팡이츠 챗봇 URL |
| 건당 대기시간(초) | 3 | 접수 건 사이 대기 |
| 요소 탐지 타임아웃(초) | 10 | 버튼 탐지 최대 대기 |
| 최대 재시도 횟수 | 3 | 실패 시 재시도 |
| 브라우저 표시 | TRUE | 브라우저 보임 여부 |
| 스크린샷 저장 | TRUE | 에러 시 캡처 |
| 사유 카테고리 | 기타 | 사유 분류 |
| 댓글 삭제 동의 | 네 | 댓글 삭제 동의 |

---

## ⚠️ 주의사항

- **처음 실행 시** 반드시 `브라우저 표시 = TRUE`로 테스트하세요
- 서버가 실행 중이어야 대시보드가 작동합니다
- Google Sheets API는 **분당 60회** 요청 제한이 있습니다
- 자동화 실행 중 시트를 수정하면 충돌이 발생할 수 있습니다
- `service_account.json`은 절대 외부에 공유하지 마세요

---

## 🔧 문제 해결

| 증상 | 원인 | 해결 |
|------|------|------|
| 서버 연결 실패 | 서버 미실행 | `python server.py` 실행 |
| 시트 연결 실패 | 서비스 계정 미설정 | Step 2 확인 |
| 시트 권한 오류 | 공유 미설정 | 서비스 계정 이메일에 편집 권한 부여 |
| 챗봇 버튼 탐지 실패 | UI 변경 | server.py의 셀렉터 업데이트 필요 |
| Playwright 오류 | 브라우저 미설치 | `playwright install chromium` |
