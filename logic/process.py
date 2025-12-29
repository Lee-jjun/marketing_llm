from datetime import datetime, timezone, timedelta
import time

from crawler.naver_cafe_pc_selenium import get_comment_and_view_pc
from utils.cafe_guard import is_cafe_post_accessible
from notion.client import update_page
from notion.fetch import (
    get_url,
    get_number,
    get_select,
    get_date,      # ✅ 노션 날짜 사용
)

BLOCKED_DOMAINS = ["gnun.link",
                   "daedamo.com",
                   "corp.babitalk.com",
                   "gangnamunni.com",
                   "sungyesa.com",
                   ]

CRAWL_MONTHS = 3
CUTOFF_DATE = datetime.now(timezone.utc) - timedelta(days=30 * CRAWL_MONTHS)


def is_blocked_url(url: str) -> bool:
    return any(domain in url for domain in BLOCKED_DOMAINS)


def process_page(page, cfg, force=False):
    print("process_page 진입:", page["id"])
    page["properties"].get("날짜")

    try:
        status = get_select(page, cfg["status"])
        if status != "대기" and not force:
            return

        url = get_url(page, cfg["url"])
        if not url:
            return

        # 🚫 크롤링 불가 도메인
        if is_blocked_url(url):
            update_page(page["id"], {
                cfg["status"]: {"status": {"name": "불가"}},
                cfg["last_run"]: {
                    "date": {"start": datetime.now(timezone.utc).isoformat()}
                }
            })
            print("🚫 불가 도메인:", url)
            return

        if not is_cafe_post_accessible(url):
            update_page(page["id"], {
                cfg["status"]: {"status": {"name": "불가"}},
                cfg["last_run"]: {
                    "date": {"start": datetime.now(timezone.utc).isoformat()}
                }
            })
            print("🚫 접근 불가:", url)
            return

        # ✅ 노션 날짜 기준 3개월 필터
        post_date = get_date(page, "날짜")  # 🔴 실제 속성명으로 변경
        if post_date and post_date < CUTOFF_DATE:
            print(
                "⏭ [SKIP: 3개월 초과]",
                f"날짜={post_date.date()}",
            )
            return

        prev_comment = get_number(page, cfg["count"]) or 0

        title, comment, view, is_deleted = get_comment_and_view_pc(url)

        if is_deleted:
            update_page(page["id"], {
                cfg["status"]: {"status": {"name": "삭제"}},
                cfg["last_run"]: {
                    "date": {"start": datetime.now(timezone.utc).isoformat()}
                }
            })
            print("🗑 삭제글:", url)
            return

        updates = {
            cfg["count"]: {"number": comment},
            cfg["view"]: {"number": view},
            cfg["last_run"]: {
                "date": {"start": datetime.now(timezone.utc).isoformat()}
            },
            cfg["status"]: {"status": {"name": "확인완료"}},
            "글 제목": {
                "rich_text": [{"text": {"content": title or ""}}]
            },
        }

        if comment > prev_comment:
            updates[cfg["new"]] = {"checkbox": True}

        update_page(page["id"], updates)
        time.sleep(0.6)

    except Exception as e:
        print("❌ ERROR PAGE:", page["id"], e)