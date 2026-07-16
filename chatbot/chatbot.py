import json
import os
import re
from pathlib import Path
from typing import Literal
from urllib.parse import quote
import urllib.request

from dotenv import load_dotenv
from fastapi import FastAPI, Query
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


BACKEND_BASE_URL = os.getenv("BACKEND_BASE_URL", "https://trapvel-backent.fly.dev")


def is_water_rocket_question(question: str) -> bool:
    q = normalize(question)
    return any(
        token in q
        for token in [
            "물로켓",
            "waterrocket",
            "waterrocketindex",
            "물로켓지수",
        ]
    )


def _fetch_json(url: str) -> dict:
    req = urllib.request.Request(url, headers={"Accept": "application/json"})
    with urllib.request.urlopen(req, timeout=15) as response:
        return json.loads(response.read().decode("utf-8"))


def extract_place_name(question: str) -> str:
    cleaned = re.sub(
        r"(물로켓지수|물로켓|지수|알려줘|해주세요|해주세요|줘|궁금|어디|점)",
        "",
        question,
    )
    cleaned = cleaned.replace("의", " ").replace("은", " ").replace("는", " ")
    cleaned = re.sub(r"[^가-힣A-Za-z0-9\s]+", " ", cleaned)
    cleaned = re.sub(r"\s+", " ", cleaned).strip()
    return cleaned


def extract_region(question: str) -> str | None:
    """
    질문에 포함된 광주 자치구 이름을 추출합니다.
    """
    regions = [
        "광산구",
        "남구",
        "동구",
        "북구",
        "서구",
    ]

    for region in regions:
        if region in question:
            return region

    return None


def _matches_region(addr1: str, region: str) -> bool:
    """
    addr1 문자열 안에서 구 이름이 공백으로 둘러싸인 형태로
    정확히 등장하는지 확인합니다.
    (예: "전남광주통합특별시 남구 서서평길 24" -> "남구" 매칭 O,
         "동구로 12" 같은 도로명 오탐은 매칭 X)
    """
    if not addr1:
        return False
    return bool(re.search(rf"(?:^|\s){re.escape(region)}(?:\s|$)", addr1))


def _find_location_by_title(title: str) -> dict | None:
    """
    백엔드의 keyword 검색을 이용해 관광지를 찾습니다.
    """
    target = normalize(title)

    if not target:
        return None

    try:
        encoded_keyword = quote(title)

        data = _fetch_json(
            f"{BACKEND_BASE_URL}/locations"
            f"?page=1"
            f"&size=100"
            f"&keyword={encoded_keyword}"
        )

    except Exception as error:
        print("=================================")
        print("관광지 이름 조회 실패")
        print("검색어:", title)
        print("오류 종류:", type(error).__name__)
        print("오류 내용:", repr(error))
        print("=================================")
        return None

    items = data.get("items") or []

    for item in items:
        item_title = normalize(item.get("title", ""))

        if item_title == target:
            return item

    for item in items:
        item_title = normalize(item.get("title", ""))

        if target in item_title or item_title in target:
            return item

    return None


def _find_locations_by_region(
    region: str,
    limit: int = 10,
) -> list[dict]:
    """
    자치구(구) 단위로 관광지를 조회합니다.

    ⚠️ 백엔드의 `/locations?region=...` 쿼리 파라미터는
    "광주_전라권" 같은 광역권 단위를 필터링하는 값이라
    "동구", "남구" 같은 자치구 이름으로는 결과가 나오지 않습니다.
    (실제 응답을 보면 모든 항목의 region 필드가 "광주_전라권"으로 동일)

    따라서 여기서는 region 파라미터를 쓰지 않고, 목록을 페이지 단위로
    가져오면서 각 항목의 addr1(주소) 문자열에서 구 이름을 직접
    찾아 필터링합니다.
    """
    matched: list[dict] = []
    page = 1
    page_size = 100  # size 최댓값

    while len(matched) < limit:
        try:
            data = _fetch_json(
                f"{BACKEND_BASE_URL}/locations"
                f"?page={page}"
                f"&size={page_size}"
            )

        except Exception as error:
            print("=================================")
            print("지역 관광지 조회 실패")
            print("지역:", region)
            print("페이지:", page)
            print("오류 종류:", type(error).__name__)
            print("오류 내용:", repr(error))
            print("=================================")
            break

        items = data.get("items") or []

        if not items:
            break

        for item in items:
            if _matches_region(item.get("addr1", ""), region):
                matched.append(item)
                if len(matched) >= limit:
                    break

        total = data.get("total", 0)
        if page * page_size >= total:
            break

        page += 1

    return matched


def fetch_water_rocket_data(question: str) -> dict | None:
    """
    물로켓 관련 질문일 때 외부 백엔드에서 데이터를 조회합니다.

    지역 질문은 addr1 기반으로 필터링해 조회하고,
    특정 관광지 질문은 /locations?keyword=... 으로 찾은 뒤
    /locations/{location_id} 상세 API를 호출합니다.
    """
    if not is_water_rocket_question(question):
        return None

    # 1. 지역 단위 질문 처리
    region = extract_region(question)

    if region:
        locations = _find_locations_by_region(
            region,
            limit=10,
        )

        if not locations:
            return {
                "status": "not_found",
                "type": "region_locations",
                "region": region,
                "locations": [],
                "message": (
                    f"{region} 관광지를 백엔드에서 찾지 못했습니다."
                ),
            }

        return {
            "status": "success",
            "type": "region_locations",
            "region": region,
            "locations": locations,
        }

    # 2. 특정 관광지 질문 처리
    place_name = extract_place_name(question)

    if place_name:
        location = _find_location_by_title(place_name)

        if location:
            location_id = location.get("id")

            if location_id is not None:
                try:
                    detail = _fetch_json(
                        f"{BACKEND_BASE_URL}/locations/{location_id}"
                    )

                    return {
                        "status": "success",
                        "type": "location_detail",
                        "searched_place_name": place_name,
                        "location": detail,
                    }

                except Exception as error:
                    print("=================================")
                    print("관광지 상세 데이터 조회 실패")
                    print("관광지:", location.get("title"))
                    print("오류 종류:", type(error).__name__)
                    print("오류 내용:", repr(error))
                    print("=================================")

            return {
                "status": "partial",
                "type": "location_summary",
                "searched_place_name": place_name,
                "location": location,
                "message": (
                    "관광지 상세 API를 조회하지 못해 "
                    "목록 API의 정보만 제공합니다."
                ),
            }

    # 3. 특정 장소나 지역을 찾지 못한 경우 최고/최저 조회
    try:
        data = _fetch_json(
            f"{BACKEND_BASE_URL}/locations/"
            f"water-rocket-extremes?limit=3"
        )

        return {
            "status": "success",
            "type": "extremes",
            "searched_place_name": place_name,
            "data": data,
        }

    except Exception as error:
        print("=================================")
        print("물로켓 최고·최저 데이터 조회 실패")
        print("오류 종류:", type(error).__name__)
        print("오류 내용:", repr(error))
        print("=================================")

        return {
            "status": "error",
            "type": "backend_error",
            "searched_place_name": place_name,
            "message": (
                "외부 백엔드에서 물로켓 데이터를 "
                "불러오지 못했습니다."
            ),
        }


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
    # 로컬 JSON에서 사용자 질문과 관련된 관광지를 검색합니다.
    places = search_places(request.message, limit=5)

    # 물로켓 질문이면 외부 백엔드 데이터를 조회합니다.
    # 여기서 바로 답변을 반환하지 않고 OpenAI에 전달할 데이터로 보관합니다.
    water_rocket_data = fetch_water_rocket_data(request.message)

    if client is None:
        return ChatResponse(
            answer=fallback_answer(request.message, places),
            places=places,
            used_ai=False,
        )

    context_data = {
        "local_places": places,
        "water_rocket_data": water_rocket_data,
    }

    context = json.dumps(
        context_data,
        ensure_ascii=False,
        indent=2,
    )

    recent_history = [
        {"role": message.role, "content": message.content}
        for message in request.history[-6:]
    ]

    try:
        response = await client.responses.create(
            model=openai_model,
            instructions=(
                "너는 광주·전라권 관광지 안내 챗봇이다. "
                "반드시 제공된 데이터만 근거로 답한다. "
                "local_places에는 로컬 관광지 검색 결과가 있다. "
                "water_rocket_data에는 외부 백엔드에서 조회한 "
                "물로켓 지수 정보가 있을 수 있다. "
                "water_rocket_data가 null이면 물로켓 질문이 아닌 것이다. "
                "물로켓 데이터가 제공된 경우 장소명, 물로켓 지수, "
                "사전 평가와 사후 평가 등의 수치를 정확하게 사용한다. "
                "type이 region_locations이면 해당 지역의 locations 목록만 사용해 답한다. "
                "물로켓 데이터의 status가 error라면 데이터를 임의로 만들지 말고 "
                "현재 외부 백엔드에서 조회하지 못했다고 안내한다. "
                "사용자가 순위, 높은 곳, 낮은 곳을 물으면 제공된 데이터 안에서 비교한다. "
                "데이터에 없는 운영시간, 요금, 평점, 후기, 인기 순위 또는 "
                "물로켓 지수를 만들지 않는다. "
                "검색 결과가 부족하면 부족하다고 분명히 말한다. "
                "사용자의 질문에 직접 답하고 한국어로 자연스럽고 간결하게 작성한다."
            ),
            input=[
                *recent_history,
                {
                    "role": "user",
                    "content": (
                        f"사용자 질문:\n{request.message}\n\n"
                        f"사용 가능한 데이터:\n{context}"
                    ),
                },
            ],
        )

        answer = response.output_text.strip()

        if not answer:
            raise ValueError("OpenAI API가 빈 답변을 반환했습니다.")

        return ChatResponse(
            answer=answer,
            places=places,
            used_ai=True,
        )

    except Exception as error:
        print("=================================")
        print("OpenAI API 호출 실패")
        print("오류 종류:", type(error).__name__)
        print("오류 내용:", repr(error))
        print("API 키 존재 여부:", bool(api_key))
        print("사용 모델:", openai_model)
        print("=================================")

        return ChatResponse(
            answer=fallback_answer(request.message, places),
            places=places,
            used_ai=False,
        )
