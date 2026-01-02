from datetime import datetime, timezone, timedelta
import time

from crawler.naver_cafe_pc_selenium import get_comment_and_view_pc
from utils.cafe_guard import is_cafe_post_accessible
from notion.client import update_page
from notion.fetch import (
    get_url,
    get_number,
    get_select,
    get_date,
)

# =========================
# 설정
# =========================
BLOCKED_DOMAINS = [
    "gnun.link",
    "daedamo.com",
    "corp.babitalk.com",
    "gangnamunni.com",
    "sungyesa.com",
]

CRAWL_MONTHS = 3
CUTOFF_DATE = datetime.now(timezone.utc) - timedelta(days=30 * CRAWL_MONTHS)

def get_block_reason(url: str) -> str | None:
    """
    크롤링 불가 사유 반환
    """
    if "gnun.link" in url:
        return "단축 URL (리다이렉트 차단)"

    if "daedamo.com" in url:
        return "대다모 (봇 차단)"

    if "corp.babitalk.com" in url:
        return "바비톡 (사내 전용 URL)"

    if "gangnamunni.com" in url:
        return "강남언니 (JS/봇 차단)"

    if "sungyesa.com" in url:
        return "성예사 (로그인/봇 차단)"

    return None

def is_blocked_url(url: str) -> bool:
    return any(domain in url for domain in BLOCKED_DOMAINS)


def process_page(page, cfg, force=False):
    print("URL 진입:", page["id"])

    try:
        # 상태
        status = get_select(page, cfg["status"])
        if status != "대기" and not force:
            return

        # URL
        url = get_url(page, cfg["url"])
        if not url:
            return

        # 🚫 크롤링 불가 사이트
        block_reason = get_block_reason(url)
        if block_reason:
            print(f"🚫 [BLOCKED] {block_reason} | URL={url}")

            update_page(
                page["id"],
                {
                    cfg["status"]: {"status": {"name": "불가"}},
                    cfg["last_run"]: {
                        "date": {"start": datetime.now(timezone.utc).isoformat()}
                    },
                    # 👉 선택사항: 노션에 사유 남기고 싶을 때
                    # "불가 사유": {
                    #     "rich_text": [{"text": {"content": block_reason}}]
                    # }
                }
            )
            return

        if not is_cafe_post_accessible(url):
            update_page(page["id"], {
                cfg["status"]: {"status": {"name": "불가"}},
                cfg["last_run"]: {"date": {"start": datetime.now(timezone.utc).isoformat()}}
            })
            return

        # 날짜 필터
        post_date = get_date(page, "날짜")
        if post_date and post_date < CUTOFF_DATE:
            print("⏭ 3개월 초과 → 스킵")
            return

        # 이전 값
        prev_total = get_number(page, cfg["count"]) or 0
        prev_external = get_number(page, "외부 댓글 수") or 0

        # 크롤링
        title, total, external, view, is_deleted = get_comment_and_view_pc(url)

        if is_deleted:
            update_page(page["id"], {
                cfg["status"]: {"status": {"name": "삭제"}},
                cfg["last_run"]: {"date": {"start": datetime.now(timezone.utc).isoformat()}}
            })
            return

        print(f"[DEBUG] total {prev_total}→{total}, external {prev_external}→{external}")

        updates = {
            cfg["count"]: {"number": total},
            "외부 댓글 수": {"number": external},
            cfg["view"]: {"number": view},
            cfg["last_run"]: {
                "date": {"start": datetime.now(timezone.utc).isoformat()}
            },
            cfg["status"]: {"status": {"name": "확인완료"}},
            "글 제목": {
                "rich_text": [{"text": {"content": title or ""}}]
            },
        }

        # ✅ NEW 알림 조건 (외부 댓글만)
        if external > prev_external:
            updates[cfg["new"]] = {"checkbox": True}

        update_page(page["id"], updates)
        time.sleep(0.6)

    except Exception as e:
        print("❌ ERROR PAGE:", page["id"], e)