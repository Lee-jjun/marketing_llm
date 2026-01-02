import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from datetime import datetime, timezone
import time
import warnings
from urllib3.exceptions import NotOpenSSLWarning
warnings.filterwarnings("ignore", category=NotOpenSSLWarning)

from config.notion_mapping import NOTION_DBS
from notion.client import (
    query_database,
    update_page,
    retrieve_page,
    retrieve_page_blocks,
    append_link_block_to_block,
)
from notion.fetch import (
    get_checkbox,
    get_url,
    get_rich_text,
    get_relation_page_ids,
    get_page_title,
    get_rollup_people_names,
)

RATE_LIMIT_SLEEP = 0.3


def find_callout_block_id(page_id: str) -> str | None:
    """
    병원 페이지에서 첫 번째 callout 블록 id 찾기
    """
    blocks = retrieve_page_blocks(page_id)
    for b in blocks:
        if b.get("type") == "callout":
            return b["id"]
    return None


def main():
    print("🔔 notify_new_comments START (후기 전용)")

    total_new = 0

    # =====================================================
    # ✅ 후기 DB만 알림 대상
    # =====================================================
    for name, cfg in NOTION_DBS.items():
        if "후기" not in name:
            continue   # ❌ 여론 완전 제외

        label = "후기"

        pages = query_database(cfg["database_id"])
        new_pages = [p for p in pages if get_checkbox(p, cfg["new"])]

        print(f"\n🔔 [{name}] NEW 페이지 수: {len(new_pages)}")
        total_new += len(new_pages)

        for page in new_pages:
            page_id = page["id"]

            try:
                # =========================
                # 게시글 정보
                # =========================
                title = get_rich_text(page, "글 제목")
                url = get_url(page, cfg["url"])

                # =========================
                # 병원 relation → 병원 페이지
                # =========================
                hospital_ids = get_relation_page_ids(page, cfg["hospital_relation"])
                if not hospital_ids:
                    print("⚠️ 병원 relation 없음 → 스킵:", page_id)
                    continue

                hospital_page_id = hospital_ids[0]

                try:
                    hospital_page = retrieve_page(hospital_page_id)
                except Exception as e:
                    print("⚠️ 병원 페이지 로드 실패 → 스킵:", hospital_page_id, e)
                    continue

                hospital_name = get_page_title(hospital_page) or "(병원명 없음)"

                # =========================
                # 담당자 (롤업)
                # =========================
                marketers = get_rollup_people_names(page, "작업자")
                marketer_text = ", ".join(marketers) if marketers else "미지정"

                print(
                    f"🏥 병원: {hospital_name} | "
                    f"[후기] 처리 중 → {page_id}"
                )

                # =========================
                # Callout 블록 찾기
                # =========================
                callout_id = find_callout_block_id(hospital_page_id)
                if not callout_id:
                    print("⚠️ Callout 블록 없음 → 스킵:", hospital_name)
                    continue

                now_text = datetime.now(timezone.utc).astimezone().strftime(
                    "%Y-%m-%d %H:%M"
                )

                # =========================
                # 🔔 알림 추가
                # =========================
                append_link_block_to_block(
                    callout_id,
                    title=f"[후기] {title or '(제목 없음)'}",
                    url=url,
                    time_text=f"{now_text} | 담당: {marketer_text}",
                )

                print(f"✅ 알림 추가 완료 → {hospital_name} (담당: {marketer_text})")

                # =========================
                # 🧹 NEW 체크 해제
                # =========================
                update_page(
                    page_id,
                    {cfg["new"]: {"checkbox": False}}
                )

                print(f"🧹 NEW 체크 해제 완료 → {page_id}")

                time.sleep(RATE_LIMIT_SLEEP)

            except Exception as e:
                print("❌ notify 처리 실패:", page_id, e)
                continue

    if total_new == 0:
        print("\n🔕 알림 대상 없음")

    print("\n🔔 notify_new_comments END")


if __name__ == "__main__":
    main()