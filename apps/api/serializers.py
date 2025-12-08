from rest_framework import serializers
from data.models import Review, ImageAsset, Campaign

class ReviewSerializer(serializers.ModelSerializer):
    class Meta:
        model = Review
        fields = "__all__"