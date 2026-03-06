from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import TokenRefreshView
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView, SpectacularRedocView
from .views import (
    RegisterView, LoginView, ForgotPasswordView,
    SkincareProductViewSet, UserRoutineViewSet, SkinProgressViewSet,
    SkinAnalysisViewSet, UserProfileViewSet, SkinHealthScoreViewSet,
    OrderViewSet, ProductReviewViewSet, NotificationViewSet, FAQViewSet
)

router = DefaultRouter()
router.register(r'products', SkincareProductViewSet)
router.register(r'routines', UserRoutineViewSet)
router.register(r'progress', SkinProgressViewSet)
router.register(r'analyze', SkinAnalysisViewSet, basename='analyze')
router.register(r'profile', UserProfileViewSet)
router.register(r'health-score', SkinHealthScoreViewSet)
router.register(r'orders', OrderViewSet)
router.register(r'reviews', ProductReviewViewSet)
router.register(r'notifications', NotificationViewSet)
router.register(r'faqs', FAQViewSet)

urlpatterns = [
    # Auth endpoints
    path('register/', RegisterView.as_view(), name='register'),
    path('login/', LoginView.as_view(), name='login'),
    path('forgot-password/', ForgotPasswordView.as_view(), name='forgot-password'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    
    # Feature endpoints
    path('', include(router.urls)),
    
    # Documentation endpoints
    path('schema/', SpectacularAPIView.as_view(), name='schema'),
    path('docs/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
    path('redoc/', SpectacularRedocView.as_view(url_name='schema'), name='redoc'),
]