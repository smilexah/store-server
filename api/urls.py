from django.urls import path, include
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView, SpectacularRedocView
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
    TokenVerifyView,
)

from api.serializers import CustomTokenObtainPairSerializer
from api.views import UserViewSet, EmailVerificationViewSet, BasketViewSet, OrderViewSet, ProductListCreateAPIView, \
    ProductRetrieveUpdateDestroyAPIView, OrderStatsAPIView, ProductCreateUpdateDestroyAPIView

app_name = 'api'

router = DefaultRouter()
router.register(r'users', UserViewSet)
router.register(r'email-verifications', EmailVerificationViewSet)
router.register(r'baskets', BasketViewSet)
router.register(r'orders', OrderViewSet)

class CustomTokenObtainPairView(TokenObtainPairView):
    serializer_class = CustomTokenObtainPairSerializer

urlpatterns = [
    path('auth/token/', CustomTokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('auth/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('auth/token/verify/', TokenVerifyView.as_view(), name='token_verify'),
    path('', include(router.urls)),
    path('products/', ProductListCreateAPIView.as_view(), name='product-list'),
    path('products/<int:pk>/', ProductRetrieveUpdateDestroyAPIView.as_view(), name='product-detail'),
    path('order-stats/', OrderStatsAPIView.as_view(), name='order-stats'),
    path('api/schema/', SpectacularAPIView.as_view(), name='schema'),
    path('api/docs/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
    path('api/redoc/', SpectacularRedocView.as_view(url_name='schema'), name='redoc'),
]