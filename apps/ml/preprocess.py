import re

PHONE_RE = re.compile(r'(\+?\d{2,3}[-.\s]?)?(\d{2,4}[-.\s]?){2,4}')
EMAIL_RE = re.compile(r'\S+@\S+\.\S+')

def clean_text(text: str) -> str:
    # 기본 정리
    t = text.strip()
    # remove urls
    t = re.sub(r'http\S+', '', t)
    # mask email/phone
    t = EMAIL_RE.sub('[EMAIL]', t)
    t = PHONE_RE.sub('[PHONE]', t)
    # normalize whitespace
    t = re.sub(r'\s+', ' ', t)
    return t