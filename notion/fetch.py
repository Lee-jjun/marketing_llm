def get_url(page, prop):
    try:
        return page["properties"][prop]["url"]
    except Exception:
        return None

def get_number(page, prop):
    try:
        return page["properties"][prop]["number"]
    except Exception:
        return None

def get_select(page, prop):
    try:
        return page["properties"][prop]["status"]["name"]
    except Exception:
        return None

def get_checkbox(page, prop):
    try:
        return page["properties"][prop]["checkbox"]
    except Exception:
        return False

def get_relation_page_ids(page, prop_name: str):
    """
    Relation 속성에 연결된 페이지 ID 리스트 반환
    """
    try:
        rel = page["properties"][prop_name]["relation"]
        return [r["id"] for r in rel]
    except Exception:
        return []

def get_page_title(page, title_prop="Name"):
    try:
        items = page["properties"][title_prop]["title"]
        return "".join(t["text"]["content"] for t in items)
    except Exception:
        return ""
    
def is_status_property(page, prop_name: str) -> bool:
    """
    해당 속성이 Status 타입인지 확인
    """
    try:
        return "status" in page["properties"][prop_name]
    except Exception:
        return False
    
def is_number_property(page, prop_name: str) -> bool:
    """
    해당 속성이 Number 타입인지 확인
    """
    try:
        return page["properties"][prop_name]["type"] == "number"
    except Exception:
        return False
    
def get_rich_text(page, prop):
    texts = page["properties"][prop]["rich_text"]
    return "".join(t["plain_text"] for t in texts)

from datetime import datetime, timezone

def get_date(page, prop):
    try:
        d = page["properties"][prop]["date"]
        if not d or not d.get("start"):
            return None

        # '2025-06-26' → datetime(UTC)
        return datetime.fromisoformat(d["start"]).replace(tzinfo=timezone.utc)

    except Exception:
        return None
    
def get_rollup_people_names(page, prop_name: str) -> list[str]:
    """
    Rollup 속성에서 People 이름 목록 추출
    """
    try:
        rollup = page["properties"][prop_name]["rollup"]
        if rollup["type"] != "array":
            return []

        names = []
        for item in rollup["array"]:
            if item["type"] == "people":
                for p in item["people"]:
                    if "name" in p:
                        names.append(p["name"])
        return names
    except Exception:
        return []
    

def get_people_ids(page, prop_name: str):
    """
    People 속성에서 사용자 ID 리스트 반환
    """
    try:
        people = page["properties"][prop_name]["people"]
        return [p["id"] for p in people]
    except Exception:
        return []