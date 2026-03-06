from django.contrib import admin
from .models import User, SkincareProduct, UserRoutine, SkinProgress, UserProfile, SkinAnalysis, SkinHealthScore, Order, ProductReview, Notification, FAQ

@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ('email',)

@admin.register(SkincareProduct)
class SkincareProductAdmin(admin.ModelAdmin):
    list_display = ('name', 'brand', 'size')

@admin.register(UserRoutine)
class UserRoutineAdmin(admin.ModelAdmin):
    list_display = ('user', 'product', 'frequency')

@admin.register(SkinProgress)
class SkinProgressAdmin(admin.ModelAdmin):
    list_display = ('user', 'logged_at')

@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'full_name', 'skin_type', 'created_at')

@admin.register(SkinAnalysis)
class SkinAnalysisAdmin(admin.ModelAdmin):
    list_display = ('user', 'overall_score', 'created_at')

@admin.register(SkinHealthScore)
class SkinHealthScoreAdmin(admin.ModelAdmin):
    list_display = ('user', 'score', 'recorded_at')

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('order_id', 'user', 'product', 'status', 'order_date')

@admin.register(ProductReview)
class ProductReviewAdmin(admin.ModelAdmin):
    list_display = ('user', 'product', 'rating', 'is_verified', 'created_at')

@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ('user', 'title', 'notification_type', 'is_read', 'created_at')

@admin.register(FAQ)
class FAQAdmin(admin.ModelAdmin):
    list_display = ('question', 'category')
