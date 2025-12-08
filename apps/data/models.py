# Review, Image, Campaign, Label models placeholder
from django.db import models
from django.db.models import JSONField

class Campaign(models.Model):
    name = models.CharField(max_length=255)
    start_date = models.DateField(null=True, blank=True)
    meta = JSONField(default=dict, blank=True)

    def __str__(self):
        return self.name

class Review(models.Model):
    campaign = models.ForeignKey(Campaign, on_delete=models.SET_NULL, null=True, blank=True)
    source = models.CharField(max_length=100, blank=True)  # ex: instagram, form
    original_text = models.TextField()
    cleaned_text = models.TextField(blank=True, null=True)
    language = models.CharField(max_length=10, default='ko')
    created_at = models.DateTimeField(auto_now_add=True)
    metadata = JSONField(default=dict, blank=True)

    # analysis outputs
    sentiment = models.CharField(max_length=32, blank=True, null=True)
    summary = models.TextField(blank=True, null=True)
    keywords = JSONField(default=list, blank=True)
    insights = JSONField(default=list, blank=True)

    def __str__(self):
        return f"Review {self.pk} - {self.source}"

class ImageAsset(models.Model):
    review = models.ForeignKey(Review, on_delete=models.CASCADE, related_name='images', null=True, blank=True)
    campaign = models.ForeignKey(Campaign, on_delete=models.SET_NULL, null=True, blank=True)
    file = models.CharField(max_length=1024)  # store S3/MinIO path or use FileField
    width = models.IntegerField(null=True, blank=True)
    height = models.IntegerField(null=True, blank=True)
    exif = JSONField(default=dict, blank=True)
    ocr_text = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    tags = JSONField(default=list, blank=True)
    caption = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"Image {self.pk}"

class Embedding(models.Model):
    # store vectors as binary? store small metadata or pointer to FAISS index
    object_type = models.CharField(max_length=32)  # 'text' or 'image'
    object_id = models.IntegerField()
    vector = models.BinaryField()  # or use a separate vector store
    created_at = models.DateTimeField(auto_now_add=True)

class Feedback(models.Model):
    review = models.ForeignKey(Review, on_delete=models.CASCADE, null=True, blank=True)
    user = models.CharField(max_length=255, blank=True)  # simple
    note = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)