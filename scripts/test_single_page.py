import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from datetime import datetime, timezone

from crawler.naver_cafe_pc_selenium import get_comment_and_view_pc
from utils.cafe_guard import is_cafe_post_accessible
from notion.client import update_page

# 🔽 테스트용 노션 페이지 ID (한 개만!)
TEST_PAGE_ID = "2cb286f326ff81b89316c04aab611d5e"

# 🔽 테스트 URL
TEST_URL = "https://cafe.naver.com/feko/999120"


def main():
    print("🧪 SINGLE PAGE + NOTION TEST START")

    if not is_cafe_post_accessible(TEST_URL):
        print("❌ 접근 불가")
        return

    title, comment, view, is_deleted = get_comment_and_view_pc(TEST_URL)

    if is_deleted:
        print("🗑 삭제된 글")
        return

    updates = {
        "댓글": {"number": comment},
        "조회수": {"number": view},
        "마지막 수집": {
            "date": {"start": datetime.now(timezone.utc).isoformat()}
        },
        "글 제목": {
            "rich_text": [{"text": {"content": title or ""}}]
        },
    }

    update_page(TEST_PAGE_ID, updates)
    print("✅ 노션 업데이트 완료")


if __name__ == "__main__":
    main()