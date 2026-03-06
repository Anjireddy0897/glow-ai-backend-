from django.core.mail import send_mail
from django.conf import settings
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, viewsets
from rest_framework.decorators import api_view
from rest_framework.permissions import AllowAny, IsAuthenticated
from .serializers import (
    RegisterSerializer, LoginSerializer, ForgotPasswordSerializer,
    SkincareProductSerializer, UserRoutineSerializer, SkinProgressSerializer,
    UserProfileSerializer, SkinAnalysisSerializer, SkinHealthScoreSerializer,
    OrderSerializer, ProductReviewSerializer, NotificationSerializer, FAQSerializer
)
from .models import User, SkincareProduct, UserRoutine, SkinProgress, UserProfile, SkinAnalysis, SkinHealthScore, Order, ProductReview, Notification, FAQ

class RegisterView(APIView):
    permission_classes = [AllowAny]
    
    def post(self, request):
        serializer = RegisterSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(
                {"message": "User registered successfully"},
                status=status.HTTP_201_CREATED
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class LoginView(APIView):
    permission_classes = [AllowAny]
    
    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        if serializer.is_valid():
            return Response(
                {
                    "message": "Login successful",
                    "tokens": serializer.validated_data.get("tokens")
                },
                status=status.HTTP_200_OK
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class ForgotPasswordView(APIView):
    permission_classes = [AllowAny]
    
    def post(self, request):
        serializer = ForgotPasswordSerializer(data=request.data)
        if serializer.is_valid():
            email = serializer.validated_data['email']
            try:
                send_mail(
                    subject="Password Reset Requested",
                    message=f"Hello,\n\nA password reset was requested for your FaceCream account ({email}).\n\nFor security reasons, we no longer send plain-text passwords. Please use the app to set a new password or contact support if you need further assistance.",
                    from_email=settings.DEFAULT_FROM_EMAIL,
                    recipient_list=[email],
                    fail_silently=False,
                )
                return Response(
                    {"message": "Password reset instructions sent to your email."},
                    status=status.HTTP_200_OK
                )
            except Exception as e:
                return Response(
                    {"error": f"Failed to send email: {str(e)}"},
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR
                )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class SkincareProductViewSet(viewsets.ModelViewSet):
    queryset = SkincareProduct.objects.all()
    serializer_class = SkincareProductSerializer
    permission_classes = [AllowAny]

    def get_queryset(self):
        queryset = super().get_queryset()
        user_id = self.request.query_params.get('user_id')
        
        if user_id:
            try:
                profile = UserProfile.objects.get(user_id=user_id)
                # Filter out allergens
                if profile.allergies:
                    allergens = [a.strip().lower() for a in profile.allergies.split(',')]
                    for allergen in allergens:
                        queryset = queryset.exclude(description__icontains=allergen)
            except UserProfile.DoesNotExist:
                pass
        
        return queryset

    def list(self, request, *args, **kwargs):
        response = super().list(request, *args, **kwargs)
        user_id = self.request.query_params.get('user_id')
        
        if user_id:
            try:
                profile = UserProfile.objects.get(user_id=user_id)
                user_skin_type = profile.skin_type.lower() if profile.skin_type else ""
                user_concerns = [c.strip().lower() for c in profile.concerns.split(',')] if profile.concerns else []

                for product_data in response.data:
                    score = 70 # Base score
                    desc = product_data['description'].lower() if product_data['description'] else ""
                    
                    # Skin type match
                    if user_skin_type in desc:
                        score += 15
                    
                    # Concerns match
                    for concern in user_concerns:
                        if concern in desc:
                            score += 5
                    
                    product_data['match_percentage'] = min(score, 99)
            except UserProfile.DoesNotExist:
                pass
        
        return response

class UserRoutineViewSet(viewsets.ModelViewSet):
    queryset = UserRoutine.objects.all()
    serializer_class = UserRoutineSerializer

    def get_queryset(self):
        user_id = self.request.query_params.get('user_id')
        if user_id:
            return self.queryset.filter(user_id=user_id)
        return self.queryset

class SkinProgressViewSet(viewsets.ModelViewSet):
    queryset = SkinProgress.objects.all()
    serializer_class = SkinProgressSerializer

    def get_queryset(self):
        user_id = self.request.query_params.get('user_id')
        if user_id:
            return self.queryset.filter(user_id=user_id)
        return self.queryset

class SkinAnalysisViewSet(viewsets.ModelViewSet):
    queryset = SkinAnalysis.objects.all()
    serializer_class = SkinAnalysisSerializer

    def perform_create(self, serializer):
        # In a real app, logic here would analyze the image.
        # For now, we generate pseudo-realistic results and save to DB.
        analysis = serializer.save(
            hydration_level=65,
            sun_damage="Low",
            acne_status="T-Zone",
            fine_lines="Mild",
            overall_score=78,
            recommendation_summary="Based on your results, we've curated personalized product recommendations for you."
        )
        # Also record a health score for tracking
        SkinHealthScore.objects.create(user=analysis.user, score=78)

    def get_queryset(self):
        user_id = self.request.query_params.get('user_id')
        if user_id:
            return self.queryset.filter(user_id=user_id)
        return self.queryset

class SkinHealthScoreViewSet(viewsets.ModelViewSet):
    queryset = SkinHealthScore.objects.all()
    serializer_class = SkinHealthScoreSerializer

    def get_queryset(self):
        user_id = self.request.query_params.get('user_id')
        if user_id:
            return self.queryset.filter(user_id=user_id).order_by('recorded_at')
        return self.queryset

class UserProfileViewSet(viewsets.ModelViewSet):
    queryset = UserProfile.objects.all()
    serializer_class = UserProfileSerializer

    def get_queryset(self):
        user_id = self.request.query_params.get('user_id')
        if user_id:
            return self.queryset.filter(user_id=user_id)
        return self.queryset

class OrderViewSet(viewsets.ModelViewSet):
    queryset = Order.objects.all()
    serializer_class = OrderSerializer

    def get_queryset(self):
        user_id = self.request.query_params.get('user_id')
        if user_id:
            return self.queryset.filter(user_id=user_id).order_by('-order_date')
        return self.queryset

class ProductReviewViewSet(viewsets.ModelViewSet):
    queryset = ProductReview.objects.all()
    serializer_class = ProductReviewSerializer

    def get_queryset(self):
        product_id = self.request.query_params.get('product_id')
        if product_id:
            return self.queryset.filter(product_id=product_id).order_by('-created_at')
        return self.queryset

class NotificationViewSet(viewsets.ModelViewSet):
    queryset = Notification.objects.all()
    serializer_class = NotificationSerializer

    def get_queryset(self):
        user_id = self.request.query_params.get('user_id')
        if user_id:
            return self.queryset.filter(user_id=user_id).order_by('-created_at')
        return self.queryset

class FAQViewSet(viewsets.ModelViewSet):
    queryset = FAQ.objects.all()
    serializer_class = FAQSerializer

    def get_queryset(self):
        category = self.request.query_params.get('category')
        if category:
            return self.queryset.filter(category=category)
        return self.queryset


@api_view(['POST'])
def recommend_products(request):

    skin_score = request.data.get("skin_score")

    if skin_score >= 80:
        product = "Vitamin C Serum"
    elif skin_score >= 60:
        product = "Niacinamide Cream"
    else:
        product = "Hydrating Moisturizer"

    return Response({
        "recommended_product": product,
        "status": "success"
    })
