from django.contrib import admin
from django.utils.html import format_html
from .models import Campaign, Review, ImageAsset, Feedback

# Register your models here.

# -------------------------------------------------------------------
#  ImageAsset Inline (Review 상세 화면에 이미지 미리보기)
# -------------------------------------------------------------------
class ImageAssetInline(admin.TabularInline):
    model = ImageAsset
    extra = 0
    readonly_fields = ('preview', 'file')

    def preview(self, obj):
        if obj.file:
            return format_html(
                '<img src="{}" style="max-height:80px; border-radius:4px"/>',
                obj.file
            )
        return "-"
    preview.short_description = "Preview"


# -------------------------------------------------------------------
#  Campaign
# -------------------------------------------------------------------
@admin.register(Campaign)
class CampaignAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'start_date')
    search_fields = ('name',)
    list_filter = ('start_date',)
    ordering = ('-start_date',)


# -------------------------------------------------------------------
#  Review
# -------------------------------------------------------------------
@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ('id', 'campaign', 'source', 'sentiment', 'created_at')
    list_filter = ('source', 'sentiment', 'created_at', 'language')
    search_fields = ('original_text', 'cleaned_text')
    readonly_fields = (
        'original_text',
        'cleaned_text',
        'summary',
        'keywords',
        'insights',
        'metadata',
        'created_at',
    )
    inlines = [ImageAssetInline]
    ordering = ('-created_at',)


# -------------------------------------------------------------------
#  ImageAsset
# -------------------------------------------------------------------
@admin.register(ImageAsset)
class ImageAssetAdmin(admin.ModelAdmin):
    list_display = ('id', 'campaign', 'review', 'thumbnail', 'created_at')
    search_fields = ('file',)
    list_filter = ('created_at',)
    readonly_fields = ('thumbnail',)

    def thumbnail(self, obj):
        if obj.file:
            return format_html(
                '<img src="{}" style="max-height:80px; border-radius:4px"/>',
                obj.file
            )
        return "-"
    thumbnail.short_description = "Preview"


# -------------------------------------------------------------------
#  Feedback
# -------------------------------------------------------------------
@admin.register(Feedback)
class FeedbackAdmin(admin.ModelAdmin):
    list_display = ('id', 'review', 'user', 'created_at')
    list_filter = ('created_at',)
    search_fields = ('note',)
    ordering = ('-created_at',)