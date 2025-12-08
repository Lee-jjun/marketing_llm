from rest_framework import serializers
from apps.data.models import Review, ImageAsset, Campaign

class ReviewSerializer(serializers.ModelSerializer):
    class Meta:
        model = Review
        fields = "__all__"