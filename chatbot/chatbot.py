import json
import os
import re
from pathlib import Path
from typing import Literal

from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from openai import AsyncOpenAI
from pydantic import BaseModel, Field

load_dotenv()

BASE_DIR = Path(__file__).resolve().parent
DATA_PATH = BASE_DIR / "data" / "tour_spots.json"
STATIC_DIR = BASE_DIR / "static"

with DATA_PATH.open("r", encoding="utf-8") as file:
    raw_data = json.load(file)

TOUR_SPOTS = raw_data["items"]

SIGUNGU_NAMES = {
    "1": "광산구",
    "2": "남구",
    "3": "동구",
    "4": "북구",
    "5": "서구",
}

CATEGORY_NAMES = {
    "NA": "자연",
    "HS": "역사·문화",
    "VE": "휴양·거리·공원",
    "EX": "체험·전시",
}

app = FastAPI(
    title="광주·전라권 관광지 챗봇",
    description="로컬 관광지 JSON 검색 결과를 OpenAI API로 자연스럽게 설명합니다.",
    version="1.0.0",
)

allowed_origins = [
    origin.strip()
    for origin in os.getenv(
        "ALLOWED_ORIGINS",
        "http://localhost:3000,http://127.0.0.1:8000,http://localhost:8000,https://ssafy16-efs-ai-onboarding.netlify.app",
    ).split(",")
    if origin.strip()
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")

api_key = os.getenv("OPENAI_API_KEY")
openai_model = os.getenv("OPENAI_MODEL", "gpt-4.1-mini")
client = AsyncOpenAI(api_key=api_key) if api_key else None


class ChatMessage(BaseModel):
    role: Literal["user", "assistant"]
    content: str = Field(min_length=1, max_length=3000)


class ChatRequest(BaseModel):
    message: str = Field(min_length=1, max_length=1000)
    history: list[ChatMessage] = Field(default_factory=list)


class ChatResponse(BaseModel):
    answer: str
    places: list[dict]
    used_ai: bool


def normalize(text: str) -> str:
    return re.sub(r"\s+", "", text).lower()


def simplify_place(item: dict) -> dict:
    return {
        "content_id": item["contentid"],
        "title": item["title"],
        "address": " ".join(
            part.strip()
            for part in [item.get("addr1", ""), item.get("addr2", "")]
            if part and part.strip()
        ),
        "district": SIGUNGU_NAMES.get(item.get("sigungucode", ""), ""),
        "category": CATEGORY_NAMES.get(item.get("lclsSystm1", ""), "기타"),
        "longitude": float(item["mapx"]),
        "latitude": float(item["mapy"]),
        "image": item.get("firstimage", ""),
    }


def score_place(item: dict, question: str) -> int:
    q = normalize(question)
    title = normalize(item.get("title", ""))
    address = normalize(item.get("addr1", "") + item.get("addr2", ""))
    district = normalize(SIGUNGU_NAMES.get(item.get("sigungucode", ""), ""))
    category = normalize(CATEGORY_NAMES.get(item.get("lclsSystm1", ""), ""))

    score = 0

    if q and q in title:
        score += 100
    if title and title in q:
        score += 90

    for token in re.findall(r"[가-힣A-Za-z0-9·]+", question):
        token = normalize(token)
        if len(token) < 2:
            continue
        if token in title:
            score += 25
        if token in address:
            score += 10
        if token in district:
            score += 15
        if token in category:
            score += 12

    keyword_categories = {
        "자연": "NA",
        "산": "NA",
        "호수": "NA",
        "폭포": "NA",
        "공원": "VE",
        "산책": "VE",
        "거리": "VE",
        "카페": "VE",
        "역사": "HS",
        "문화재": "HS",
        "사찰": "HS",
        "절": "HS",
        "체험": "EX",
        "전시": "EX",
    }

    for keyword, code in keyword_categories.items():
        if keyword in question and item.get("lclsSystm1") == code:
            score += 20

    for code, name in SIGUNGU_NAMES.items():
        if name in question and item.get("sigungucode") == code:
            score += 25

    return score


def search_places(question: str, limit: int = 5) -> list[dict]:
    ranked = sorted(
        ((score_place(item, question), item) for item in TOUR_SPOTS),
        key=lambda pair: pair[0],
        reverse=True,
    )

    matched = [simplify_place(item) for score, item in ranked if score > 0][:limit]

    if not matched:
        # 검색 조건이 전혀 없을 때 데모용 대표 관광지를 반환합니다.
        preferred = ["무등산 주상절리대", "충장로", "풍암호수", "동리단길 카페거리", "광주호"]
        lookup = {item["title"]: simplify_place(item) for item in TOUR_SPOTS}
        matched = [lookup[name] for name in preferred if name in lookup][:limit]

    return matched


def fallback_answer(question: str, places: list[dict]) -> str:
    lines = ["현재 관광지 데이터에서 다음 장소를 찾았습니다."]
    for index, place in enumerate(places, start=1):
        lines.append(
            f"{index}. {place['title']} — {place['category']}, "
            f"{place['district']}, {place['address']}"
        )
    lines.append(
        "\n현재는 이름·주소·분류·좌표 기반 검색만 가능합니다. "
        "평점, 리뷰, 물로켓 지수는 데이터가 추가되어야 안내할 수 있습니다."
    )
    return "\n".join(lines)


@app.get("/")
async def index():
    return FileResponse(STATIC_DIR / "index.html")


@app.get("/health")
async def health():
    return {
        "status": "ok",
        "tour_spot_count": len(TOUR_SPOTS),
        "openai_enabled": client is not None,
        "openai_key_configured": bool(api_key),
        "openai_model": openai_model,
    }


@app.get("/api/places")
async def places(
    keyword: str = Query(default="", max_length=100),
    limit: int = Query(default=10, ge=1, le=30),
):
    return {
        "total": len(TOUR_SPOTS),
        "items": search_places(keyword, limit),
    }


@app.post("/api/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    places = search_places(request.message, limit=5)

    if client is None:
        return ChatResponse(
            answer=fallback_answer(request.message, places),
            places=places,
            used_ai=False,
        )

    context = json.dumps(places, ensure_ascii=False, indent=2)
    recent_history = [
        {"role": message.role, "content": message.content}
        for message in request.history[-6:]
    ]

    try:
        response = await client.responses.create(
            model=openai_model,
            instructions=(
                "너는 광주·전라권 관광지 안내 챗봇이다. "
                "반드시 제공된 검색 결과만 근거로 답한다. "
                "데이터에 없는 운영시간, 요금, 평점, 후기, 인기 순위, 물로켓 지수를 만들지 않는다. "
                "사용자의 취향과 검색 결과를 연결하여 2~5개 장소를 간결하게 추천한다. "
                "주소와 분류가 유용하면 함께 안내한다. "
                "검색 결과가 부족하면 부족하다고 분명히 말한다. 한국어로 답한다."
            ),
            input=[
                *recent_history,
                {
                    "role": "user",
                    "content": (
                        f"사용자 질문:\n{request.message}\n\n"
                        f"로컬 관광지 검색 결과:\n{context}"
                    ),
                },
            ],
        )

        answer = response.output_text.strip()
        if not answer:
            raise ValueError("OpenAI API가 빈 답변을 반환했습니다.")

        return ChatResponse(answer=answer, places=places, used_ai=True)

    except Exception as error:
        print(f"OpenAI API error: {error}")
        return ChatResponse(
            answer=fallback_answer(request.message, places),
            places=places,
            used_ai=False,
        )
