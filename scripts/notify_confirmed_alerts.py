import sys
import os
import time

# =========================
# 📌 경로 세팅 (config import 오류 방지)
# =========================
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, BASE_DIR)

from config.notion_mapping import NOTION_DBS
from notion.client import (
    query_database,
    update_page,
    retrieve_page_blocks,
    delete_block,
)
from notion.fetch import (
    get_checkbox,
    get_relation_page_ids,
)

# =========================
# ⏱ 설정값
# =========================
RATE_LIMIT = 0.5  # Notion DELETE 안정성 확보
PRINT_PREFIX = "🧹"

# =========================
# 🏥 병원 DB 설정
# =========================
HOSPITAL_DB_ID = "1f2286f326ff809ba734eadac7ab8c66"   # 병원(업체 리스트) DB ID
HOSPITAL_CONFIRM_PROP = "알림 확인 완료"            # 체크박스 속성명


# =========================
# 🔔 알림 전용 Callout 찾기
# =========================
def find_alert_callout_block(page_id: str):
    """
    🔔 또는 '알림' 텍스트가 포함된 Callout 1개만 찾는다
    """
    try:
        blocks = retrieve_page_blocks(page_id)
    except Exception as e:
        print("❌ 병원 블록 조회 실패:", page_id, e)
        return None

    for b in blocks:
        if b.get("type") != "callout":
            continue

        callout = b.get("callout", {})
        rich_texts = callout.get("rich_text", [])

        text = "".join(t.get("plain_text", "") for t in rich_texts)

        if "🔔" in text or "알림" in text:
            return b["id"]

    return None


# =========================
# 🛡 안전한 블록 삭제
# =========================
def safe_delete_block(block_id: str):
    try:
        delete_block(block_id)
        time.sleep(RATE_LIMIT)
    except Exception as e:
        # ❗ 삭제 실패해도 절대 중단하지 않음
        print("⚠️ 블록 삭제 실패 (무시):", block_id, e)


# =========================
# 🚀 main
# =========================
def main():
    print(f"{PRINT_PREFIX} notify_confirmed_alerts START")

    # 1️⃣ 병원 DB 조회
    hospitals = query_database(HOSPITAL_DB_ID)
    targets = [h for h in hospitals if get_checkbox(h, HOSPITAL_CONFIRM_PROP)]

    print(f"{PRINT_PREFIX} 알림 정리 대상 병원 수: {len(targets)}")

    if not targets:
        print("🔕 정리 대상 없음 → 종료")
        return

    # 2️⃣ 병원별 처리
    for hospital in targets:
        hospital_id = hospital["id"]
        print(f"\n🏥 병원 처리 시작: {hospital_id}")

        # =========================
        # A. 🔔 알림 Callout만 정리
        # =========================
        alert_callout_id = find_alert_callout_block(hospital_id)

        if not alert_callout_id:
            print("⚠️ 알림 콜아웃 없음 → 스킵")
        else:
            try:
                children = retrieve_page_blocks(alert_callout_id)
            except Exception as e:
                print("⚠️ 알림 콜아웃 children 조회 실패:", e)
                children = []

            for c in children:
                safe_delete_block(c["id"])

            print("🧹 알림 콜아웃 정리 완료")

        # =========================
        # B. 여론 / 후기 NEW 해제
        # =========================
        for name, cfg in NOTION_DBS.items():
            if "여론" not in name and "후기" not in name:
                continue

            try:
                pages = query_database(cfg["database_id"])
            except Exception as e:
                print("⚠️ DB 조회 실패:", name, e)
                continue

            for p in pages:
                if not get_checkbox(p, cfg["new"]):
                    continue

                hospital_ids = get_relation_page_ids(p, cfg["hospital_relation"])
                if hospital_id not in hospital_ids:
                    continue

                try:
                    update_page(
                        p["id"],
                        {cfg["new"]: {"checkbox": False}}
                    )
                    time.sleep(RATE_LIMIT)
                except Exception as e:
                    print("⚠️ NEW 체크 해제 실패:", p["id"], e)

        print("🧹 여론/후기 NEW 체크 해제 완료")

        # =========================
        # C. 병원 알림 확인 체크 해제
        # =========================
        try:
            update_page(
                hospital_id,
                {HOSPITAL_CONFIRM_PROP: {"checkbox": False}}
            )
            print("☑ 알림 확인 체크 해제 완료")
        except Exception as e:
            print("❌ 알림 확인 체크 해제 실패:", hospital_id, e)

        time.sleep(RATE_LIMIT)

    print(f"\n{PRINT_PREFIX} notify_confirmed_alerts END")


if __name__ == "__main__":
    main()