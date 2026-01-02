from __future__ import annotations

import re
import time

from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from selenium.common.exceptions import (
    TimeoutException,
    WebDriverException,
    UnexpectedAlertPresentException,
    NoAlertPresentException,
)

from crawler.driver import get_driver, quit_driver


# =========================
# Alert 처리
# =========================
def _try_accept_alert(driver) -> str:
    try:
        alert = driver.switch_to.alert
        text = (alert.text or "").strip()
        alert.accept()
        return text
    except NoAlertPresentException:
        return ""
    except Exception:
        return ""


def _is_deleted_alert(text: str) -> bool:
    t = text.replace("\n", " ").strip()
    return ("삭제" in t) or ("존재하지" in t) or ("삭제되었" in t)


# =========================
# 작성자 댓글 판별
# =========================
def _is_author_comment(comment_el) -> bool:
    try:
        # 1️⃣ 텍스트 기반
        if "작성자" in comment_el.text:
            return True

        # 2️⃣ class / badge 기반
        badges = comment_el.find_elements(
            By.XPATH,
            ".//*[contains(@class,'writer') or contains(@class,'author')]"
        )
        if badges:
            return True

        # 3️⃣ aria-label
        aria = comment_el.get_attribute("aria-label") or ""
        if "작성자" in aria:
            return True

        return False
    except Exception:
        return False


# =========================
# 메인 크롤러
# =========================
def get_comment_and_view_pc(url: str):
    """
    return:
    (
        title: str,
        total_comment: int,        # 전체 댓글 수
        external_comment: int,     # 작성자 제외 댓글 수
        view: int,
        is_deleted: bool
    )
    """
    driver = get_driver()
    print("▶ 접속 URL(PC):", url)

    try:
        driver.set_page_load_timeout(20)
        driver.switch_to.default_content()
        driver.get(url)

        # alert 선처리
        alert_text = _try_accept_alert(driver)
        if alert_text:
            if _is_deleted_alert(alert_text):
                quit_driver()
                return "", 0, 0, 0, True
            quit_driver()
            return "", 0, 0, 0, False

        wait = WebDriverWait(driver, 15)
        wait.until(EC.frame_to_be_available_and_switch_to_it((By.ID, "cafe_main")))
        time.sleep(0.7)

        html = driver.page_source

        # 제목
        title = ""
        for sel in ["h3.title_text", "strong.title_text", "div.title_text"]:
            try:
                el = driver.find_element(By.CSS_SELECTOR, sel)
                title = el.text.strip()
                if title:
                    break
            except Exception:
                pass

        # 조회수
        view = 0
        m_view = re.search(r"조회\s*([0-9,]+)", html)
        if m_view:
            view = int(m_view.group(1).replace(",", ""))

        # 댓글 DOM 탐색 (다중 셀렉터)
        COMMENT_SELECTORS = [
            "li.comment_item",
            "li.CommentItem",
            "div.comment_box li",
            "div.comment_area li",
        ]

        comment_elements = []
        for sel in COMMENT_SELECTORS:
            try:
                comment_elements = driver.find_elements(By.CSS_SELECTOR, sel)
                if comment_elements:
                    break
            except Exception:
                continue

        # 댓글 수 계산
        if comment_elements:
            total_comment = len(comment_elements)
            external_comment = 0
            for c in comment_elements:
                if not _is_author_comment(c):
                    external_comment += 1
        else:
            # fallback (DOM 못잡을 때)
            m_comment = re.search(r"댓글\s*([0-9,]+)", html)
            total_comment = int(m_comment.group(1).replace(",", "")) if m_comment else 0
            external_comment = total_comment  # 작성자 구분 불가 → 전체로 처리

        print(
            f"✅ 결과 → 제목:{title} | "
            f"전체:{total_comment} | 외부:{external_comment} | 조회:{view}"
        )

        return title, total_comment, external_comment, view, False

    except UnexpectedAlertPresentException:
        text = _try_accept_alert(driver)
        if _is_deleted_alert(text):
            quit_driver()
            return "", 0, 0, 0, True
        quit_driver()
        return "", 0, 0, 0, False

    except (TimeoutException, WebDriverException) as e:
        print("⚠️ Selenium 오류:", e)
        quit_driver()
        return "", 0, 0, 0, False

    except Exception as e:
        print("❌ 크롤링 실패:", e)
        quit_driver()
        return "", 0, 0, 0, False

    finally:
        try:
            driver.switch_to.default_content()
        except Exception:
            pass