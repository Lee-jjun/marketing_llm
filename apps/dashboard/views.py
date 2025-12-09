from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse
from apps.data.models import Review, Campaign, ImageAsset
from apps.ml.services.llm_service import generate_review

def index(request):
    total_reviews = Review.objects.count()
    generated = Review.objects.filter(metadata__generated_by='llm').count()
    campaigns = Campaign.objects.all()[:6]
    context = {
        "total_reviews": total_reviews,
        "generated_reviews": generated,
        "model_version": "A-1.0",
        "campaigns": campaigns
    }
    return render(request, "dashboard/index.html", context)

def upload_view(request):
    return render(request, "dashboard/upload.html")

def review_list(request):
    reviews = Review.objects.all().order_by("-created_at")[:200]
    return render(request, "dashboard/review_list.html", {"reviews": reviews})

def review_detail(request, pk):
    review = get_object_or_404(Review, pk=pk)
    return render(request, "dashboard/review_detail.html", {"r": review})

def review_generate(request):
    if request.method == 'GET':
        return render(request, "dashboard/review_generate.html")
    # POST: create via LLM
    clinic = request.POST.get("hospital")
    service = request.POST.get("service")
    tone = request.POST.get("tone", "친절한 톤")
    if not clinic or not service:
        return JsonResponse({"error":"hospital and service required"}, status=400)
    try:
        generated = generate_review(clinic_name=clinic, treatment=service, tone=tone)
    except Exception as e:
        return JsonResponse({"error":"LLM failed","detail":str(e)}, status=500)
    rev = Review.objects.create(original_text=generated, cleaned_text=generated[:1000], metadata={"generated_by":"llm","clinic":clinic})
    return JsonResponse({"review":generated,"review_id":rev.id})
    
def image_browser(request):
    images = ImageAsset.objects.all().order_by("-created_at")[:200]
    return render(request, "dashboard/image_browser.html", {"images": images})