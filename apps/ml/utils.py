"""
Compatibility shim for ML utilities.

This module provides small wrappers so other modules can import
`apps.ml.utils`. Implementations are placeholders — replace with
real implementations (model calls, embeddings, etc.) as needed.
"""
from .preprocess import clean_text

def get_text_embedding(text):
    """Return a placeholder text embedding.

    Replace with a real embedding extractor (OpenAI/other model).
    """
    raise NotImplementedError("get_text_embedding is not implemented. Implement or wire to an embedding service.")

def get_image_embedding(file_obj):
    """Return a placeholder image embedding.

    Replace with a real image embedding extractor.
    """
    raise NotImplementedError("get_image_embedding is not implemented. Implement or wire to an image embedding service.")

def call_llm_summary(text):
    """Return a placeholder summary using LLM.

    Replace with a call to `apps.ml.services.llm_service` or other LLM wrapper.
    """
    raise NotImplementedError("call_llm_summary is not implemented. Implement LLM summarization.")

def call_sentiment(text):
    """Return a placeholder sentiment result.

    Replace with a real sentiment classifier.
    """
    raise NotImplementedError("call_sentiment is not implemented. Implement sentiment analysis.")
