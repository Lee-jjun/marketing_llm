import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from datetime import datetime, timedelta, timezone
import time

from notion.client import query_database, update_page
from notion.fetch import (
    get_relation_page_ids,
    get_date,
)

from config.notion_mapping import NOTION_DBS

# =========================
# ⏱ 설정값
# =========================
RATE_LIMIT_SLEEP = 0.3
LOOKBACK_DAYS = 7  # 최근 N일 업무일지만 확인

# =========================
# 📘 병원별 데일리 업무일지 DB 목록
# =========================
DAILY_WORKLOG_DBS = {
    "봄빛병원": "25b286f326ff81e59d46d5c3d80b7271",
    "윈느성형외과": "2ca286f326ff818e9160e8ba8840ab9b",
    "밸런스랩성형외과": "21d286f326ff8178a9c2f732e1b15aa9",
    "신상성형외과": "21c286f326ff812885a9e95bb89ffb7a",
    "히트성형외과": "223286f326ff81b0b185f2c518b00b11",
    "다름성형외과": "23f286f326ff819fa26fd68f7668d3d0",
    "지힐링스퀘어": "242286f326ff812e871eecd09e97bccd",
    "아우어성형외과": "242286f326ff812e871eecd09e97bccd",
    "강남12의원": "223286f326ff816e80d8cb2e056c3c81",
    "프리마성형외과": "295286f326ff81e6a321ff6926edd515",
    "A&A": "223286f326ff813eb703cf4791153bf6",
    "서진성형외과": "2b2286f326ff816dbeaac544dd59a56c",
    "라라성형외과": "2b2286f326ff8139a997fdfb8f4617cc",
    "사치바이오": "233286f326ff81aa92aaceeb5511a73e",
    "PHD피부과": "2d1286f326ff810b9cf9c41a8d57ecba",
    "혜빈씨 연습용": "2ce286f326ff81d5b1c4c5e155f4e06c",
}

# =========================
# 📘 속성명
# =========================
DAILY_HOSPITAL_PROP = "병원 연동"   # Relation → 병원 DB
DAILY_DATE_PROP = "날짜"            # Date
POST_DATE_PROP = "날짜"             # Date


def same_day(d1, d2):
    if not d1 or not d2:
        return False
    return d1.date() == d2.date()


def extract_hospital_from_db_name(db_name: str):
    """
    여론/후기 DB 이름에서 병원명 추출
    예: '봄빛병원 후기' → '봄빛병원'
    """
    for hospital_name in DAILY_WORKLOG_DBS.keys():
        if hospital_name in db_name:
            return hospital_name
    return None


def main():
    print("\n🔁 auto_link_hospital START\n")

    cutoff = datetime.now(timezone.utc) - timedelta(days=LOOKBACK_DAYS)

    # =========================
    # 1️⃣ 최근 데일리 업무일지 수집
    # =========================
    recent_daily = []

    for hospital_name, db_id in DAILY_WORKLOG_DBS.items():
        try:
            pages = query_database(db_id)
        except Exception as e:
            print(f"❌ 업무일지 DB 조회 실패: {hospital_name}", e)
            continue

        for p in pages:
            daily_date = get_date(p, DAILY_DATE_PROP)
            hospital_ids = get_relation_page_ids(p, DAILY_HOSPITAL_PROP)

            if not daily_date:
                continue
            if daily_date < cutoff:
                continue
            if not hospital_ids:
                continue

            p["_source_hospital"] = hospital_name
            recent_daily.append(p)

    print(f"📘 최근 업무일지 수집 완료: {len(recent_daily)}건")

    if not recent_daily:
        print("⛔ 기준 업무일지 없음 → 종료")
        return

    # =========================
    # 2️⃣ 여론 / 후기 DB 순회
    # =========================
    for name, cfg in NOTION_DBS.items():
        if "여론" not in name and "후기" not in name:
            continue

        current_hospital = extract_hospital_from_db_name(name)
        if not current_hospital:
            print(f"⚠️ 병원명 추출 실패 → {name}")
            continue

        print(f"\n📕 처리 중: {name} (병원={current_hospital})")

        try:
            pages = query_database(cfg["database_id"])
        except Exception as e:
            print(f"❌ DB 조회 실패: {name}", e)
            continue

        for page in pages:
            page_id = page["id"]

            page_date = get_date(page, POST_DATE_PROP)
            if not page_date:
                continue

            # 기존 병원 Relation
            existing_ids = set(
                get_relation_page_ids(page, cfg["hospital_relation"])
            )

            matched_ids = set()

            for daily in recent_daily:
                daily_date = get_date(daily, DAILY_DATE_PROP)

                if (
                    same_day(page_date, daily_date)
                    and daily.get("_source_hospital") == current_hospital
                ):
                    daily_hospital_ids = get_relation_page_ids(
                        daily, DAILY_HOSPITAL_PROP
                    )
                    matched_ids.update(daily_hospital_ids)

            new_ids = matched_ids - existing_ids

            if not new_ids:
                continue

            update_page(
                page_id,
                {
                    cfg["hospital_relation"]: {
                        "relation": [
                            {"id": hid}
                            for hid in (existing_ids | new_ids)
                        ]
                    }
                }
            )

            print(
                f"🔗 병원 연결 완료 → page={page_id} | "
                f"병원={current_hospital}"
            )

            time.sleep(RATE_LIMIT_SLEEP)

    print("\n🔁 auto_link_hospital END\n")


if __name__ == "__main__":
    main()