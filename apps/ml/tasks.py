from celery import shared_task
from apps.data.models import Review, ImageAsset
from apps.ml.utils import clean_text, get_text_embedding, get_image_embedding, call_llm_summary, call_sentiment

@shared_task
def analyze_review_task(review_id):
    r = Review.objects.get(pk=review_id)
    # 1) 전처리
    cleaned = clean_text(r.original_text)
    r.cleaned_text = cleaned
    r.save()

    # 2) LLM 요약 (가능하면 내부 모델 호출 or external API)
    summary = call_llm_summary(cleaned)
    r.summary = summary

    # 3) sentiment
    sentiment = call_sentiment(cleaned)
    r.sentiment = sentiment

    # 4) keywords / insights (prompt-based)
    # save keywords,insights as lists
    r.keywords = ["예시키워드1","예시키워드2"]
    r.insights = ["핵심 인사이트 예시"]
    r.save()

    # 5) embeddings
    emb = get_text_embedding(cleaned)
    # push emb to FAISS (or save Embedding model)
    from apps.ml.vector_store import add_vector_to_index
    add_vector_to_index('text', r.id, emb)

    # image path: generate image embeddings for linked images
    for img in r.images.all():
        image_emb = get_image_embedding(img.file)
        add_vector_to_index('image', img.id, image_emb)