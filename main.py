from utils.run_lock import acquire_lock, release_lock

from config.notion_mapping import NOTION_DBS
from notion.client import query_database, update_page
from notion.fetch import get_checkbox
from logic.process import process_page

import traceback

try:
    acquire_lock()

    for name, cfg in NOTION_DBS.items():
        print(f"\n===== DB 처리 시작: {name} =====")

        try:
            pages = query_database(cfg["database_id"])
        except Exception as e:
            print("❌ DB 조회 실패:", e)
            continue   # 🔥 다음 DB로 넘어감

        print(f"[DB] {name} 페이지 수:", len(pages))

        # =========================
        # 🔑 refresh flag 안전 처리
        # =========================
        refresh_flag_prop = cfg.get("db_refresh_flag")

        if refresh_flag_prop:
            try:
                force = any(
                    get_checkbox(p, refresh_flag_prop)
                    for p in pages
                )
            except Exception as e:
                print("⚠️ refresh flag 체크 실패 → force=False", e)
                force = False
        else:
            force = False

        for idx, page in enumerate(pages, start=1):
            print(f"[{idx}/{len(pages)}] processing")
            try:
                process_page(page, cfg, force=force)
            except Exception as e:
                print("❌ process_page 에러:", page["id"], e)
                traceback.print_exc()
                continue   # 🔥 절대 멈추지 않음

        # =========================
        # refresh flag 해제 (있는 DB만)
        # =========================
        if force and refresh_flag_prop:
            print("🔄 refresh flag 해제 중...")
            for p in pages:
                try:
                    update_page(
                        p["id"],
                        {
                            refresh_flag_prop: {"checkbox": False}
                        }
                    )
                except Exception as e:
                    print("⚠️ refresh flag 해제 실패:", p["id"], e)
                    continue

        print(f"===== DB 처리 종료: {name} =====")

finally:
    release_lock()