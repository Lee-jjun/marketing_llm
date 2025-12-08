from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import ReviewViewSet, ReviewGenerateAPI, UploadView

router = DefaultRouter()
router.register("reviews", ReviewViewSet)

urlpatterns = [
    path("", include(router.urls)),
    path("upload/", UploadView.as_view()),
    path("generate-review/", ReviewGenerateAPI.as_view()),
]