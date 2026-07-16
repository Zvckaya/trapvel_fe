# 광주·전라권 관광지 FastAPI 챗봇

업로드된 관광지 JSON 505개를 로컬에서 검색한 뒤, 검색된 관광지만 OpenAI API에 전달해 자연어 답변을 생성하는 최소 예제입니다.

## 지금 가능한 기능

- 관광지 이름 검색
- 광산구·남구·동구·북구·서구 조건 검색
- 자연 / 역사·문화 / 공원·거리 / 체험 유형 추천
- 주소, 좌표, 이미지 표시
- OpenAI API가 없을 때도 로컬 검색 모드로 실행

평점, 리뷰, 운영시간, 요금, 인기도, 물로켓 지수는 현재 JSON에 없으므로 제공하지 않습니다.

## 1. 설치

```bash
python -m venv .venv
```

Windows PowerShell:

```powershell
.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

## 2. API 키 설정

`.env.example`을 복사해서 `.env`를 만듭니다.

```env
OPENAI_API_KEY=여기에_API_키
OPENAI_MODEL=gpt-5.5
```

API 키 없이도 검색 기능은 동작합니다.

## 3. 실행

```bash
uvicorn main:app --reload
```

- 채팅 화면: http://127.0.0.1:8000
- API 문서: http://127.0.0.1:8000/docs
- 상태 확인: http://127.0.0.1:8000/health

## API 예시

`POST /api/chat`

```json
{
  "message": "동구에서 산책하기 좋은 곳 추천해줘",
  "history": []
}
```

## 구현 구조

1. 질문에서 관광지명·구·유형 키워드를 찾습니다.
2. 로컬 JSON 505개를 점수화해 상위 5개를 선택합니다.
3. 선택된 5개 데이터만 OpenAI API에 전달합니다.
4. 모델은 해당 데이터만 근거로 답변합니다.

이 구조는 JSON 전체를 매번 API에 보내지 않으므로 비용과 환각 가능성을 줄입니다.
