from django.shortcuts import render, get_object_or_404
from django.views import View
from django.http import JsonResponse
from apps.data.models import Review, Campaign

def index(request):
    return render(request, "dashboard/index.html")

def upload_view(request):
    return render(request, "dashboard/upload.html")

def review_list(request):
    reviews = Review.objects.all().order_by("-id")
    return render(request, "dashboard/review_list.html", {"reviews": reviews})

def review_detail(request, pk):
    review = Review.objects.get(pk=pk)
    return render(request, "dashboard/review_detail.html", {"review": review})

def review_generate(request):
    return render(request, "dashboard/review_generate.html")

def image_browser(request):
    return render(request, "dashboard/image_browser.html")