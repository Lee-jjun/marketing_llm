import openai
from django.conf import settings

openai.api_key = settings.OPENAI_API_KEY

def generate_review(clinic_name: str, treatment: str, tone: str = "친절한 후기 스타일"):
    prompt = f"""
    병의원 바이럴 리뷰 작성.

    병원명: {clinic_name}
    시술: {treatment}
    톤: {tone}

    조건:
    - 실제 후기처럼 자연스럽게 작성
    - 과장 광고 금지
    - 부정적인 내용 없이 긍정적으로 설명
    - 최소 5문장 이상
    """

    response = openai.chat.completions.create(
        model="gpt-4o-mini",   # 비용 저렴하고 속도 빠름
        messages=[
            {"role": "user", "content": prompt}
        ],
        max_tokens=300,
        temperature=0.7,
    )

    result = response.choices[0].message.content
    return result