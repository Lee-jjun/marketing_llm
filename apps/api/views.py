from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework import viewsets
from rest_framework.serializers import ModelSerializer

from apps.data.models import Review
from apps.ml.tasks import analyze_review_task
from apps.ml.services.llm_service import generate_review


class UploadView(APIView):
    def post(self, request):
        text = request.data.get('text')
        images = request.data.get('images', [])
        campaign_id = request.data.get('campaign_id')

        review = Review.objects.create(original_text=text, campaign_id=campaign_id)

        # TODO: 이미지 저장 / ImageAsset 생성

        analyze_review_task.delay(review.id)  # celery task
        return Response({'review_id': review.id}, status=status.HTTP_201_CREATED)



# -----------------------------
# Review CRUD (ViewSet)
# -----------------------------
class ReviewSerializer(ModelSerializer):
    class Meta:
        model = Review
        fields = "__all__"

class ReviewViewSet(viewsets.ModelViewSet):
    queryset = Review.objects.all().order_by("-id")
    serializer_class = ReviewSerializer



# -----------------------------
# Review Generate LLM API
# -----------------------------
class ReviewGenerateAPI(APIView):
    def post(self, request):
        clinic = request.data.get("clinic")
        treatment = request.data.get("treatment")
        tone = request.data.get("tone", "20대 여성 후기 스타일")

        if not clinic or not treatment:
            return Response({"error": "clinic, treatment 필수"}, status=400)

        review_text = generate_review(clinic, treatment, tone)

        return Response({
            "clinic": clinic,
            "treatment": treatment,
            "tone": tone,
            "review": review_text
        })