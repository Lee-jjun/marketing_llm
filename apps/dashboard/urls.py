from django.urls import path
from . import views

app_name = "dashboard"

urlpatterns = [
    path("", views.index, name="index"),
    path("upload/", views.upload_view, name="upload"),
    path("reviews/", views.review_list, name="review_list"),
    path("reviews/<int:pk>/", views.review_detail, name="review_detail"),
    path("generate/", views.review_generate, name="review_generate"),
    path("images/", views.image_browser, name="image_browser"),
]