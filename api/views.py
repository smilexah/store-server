from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import extend_schema_view, extend_schema, OpenApiParameter, OpenApiExample, OpenApiResponse
from rest_framework import status, viewsets, generics, permissions
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework.response import Response
from rest_framework.exceptions import PermissionDenied, ValidationError
from django.shortcuts import get_object_or_404
from rest_framework.views import APIView
from rest_framework_simplejwt.authentication import JWTAuthentication

from api.permissions import IsAdminOrReadOnly, IsProductOwnerOrAdmin, IsOrderOwnerOrAdmin
from orders.models import Order, OrderStatus, OrderItem
from orders.serializers import OrderSerializer
from products.models import Product, Basket
from products.serializers import BasketSerializer, ProductSerializer
from users.models import EmailVerificationStatus, EmailVerification, User
from users.serializers import EmailVerificationSerializer, UserSerializer


@extend_schema(
    summary="Order statistics",
    description="Get detailed statistics about user's orders",
    responses={
        200: OpenApiResponse(
            description="Successful response",
            examples={
                "application/json": {
                    "total_orders": 5,
                    "total_spent": 499.95,
                    "pending_orders": 2
                }
            }
        ),
        401: OpenApiResponse(
            description="Unauthorized",
            examples={
                "application/json": {
                    "detail": "Authentication credentials were not provided."
                }
            }
        )
    }
)
class OrderStatsAPIView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user_orders = Order.objects.filter(initiator=request.user)

        stats = {
            'total_orders': user_orders.count(),
            'total_spent': sum(order.basket_history['total_sum'] for order in user_orders),
            'pending_orders': user_orders.filter(status=OrderStatus.CREATED).count(),
        }

        return Response(stats, status=status.HTTP_200_OK)


class ProductCreateUpdateDestroyAPIView(generics.RetrieveUpdateDestroyAPIView):
    authentication_classes = [JWTAuthentication]
    queryset = Product.objects.select_related('category')
    serializer_class = ProductSerializer
    lookup_field = 'pk'

    def get_permissions(self):
        if self.request.method == 'GET':
            return [permissions.AllowAny()]
        elif self.request.method in ['PUT', 'PATCH']:
            return [IsAuthenticated(), IsProductOwnerOrAdmin()]
        return [IsAdminUser()]

    def perform_update(self, serializer):
        instance = serializer.save()
        if 'quantity' in serializer.validated_data:
            if serializer.validated_data['quantity'] == 0:
                instance.is_active = False
                instance.save()

    def perform_destroy(self, instance):
        instance.is_active = False
        instance.save()


class ProductListCreateAPIView(generics.ListCreateAPIView):
    queryset = Product.objects.select_related('category')
    serializer_class = ProductSerializer
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAdminOrReadOnly]

    def get_queryset(self):
        return super().get_queryset().select_related('category').prefetch_related('category__products')


class ProductRetrieveUpdateDestroyAPIView(generics.RetrieveUpdateDestroyAPIView):
    authentication_classes = [JWTAuthentication]
    queryset = Product.objects.select_related('category')
    serializer_class = ProductSerializer

    def get_permissions(self):
        if self.request.method == 'GET':
            return [permissions.AllowAny()]
        elif self.request.method in ['PUT', 'PATCH']:
            return [IsAuthenticated(), IsProductOwnerOrAdmin()]
        return [IsAdminUser()]  # DELETE only for admins


class BasketViewSet(viewsets.GenericViewSet,
                    generics.mixins.ListModelMixin,
                    generics.mixins.RetrieveModelMixin,
                    generics.mixins.CreateModelMixin,
                    generics.mixins.UpdateModelMixin,
                    generics.mixins.DestroyModelMixin):
    queryset = Basket.objects.all().select_related('product', 'product__category')
    serializer_class = BasketSerializer
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]
    pagination_class = None

    def get_queryset(self):
        return Basket.objects.filter(
            user=self.request.user
        ).select_related('product', 'product__category')

    def perform_create(self, serializer):
        product_id = self.request.data.get('product_id')
        product = get_object_or_404(Product, id=product_id)
        basket, _ = Basket.create_or_update(product.id, self.request.user)
        serializer.instance = basket

    def perform_update(self, serializer):
        if 'quantity' in serializer.validated_data:
            if serializer.validated_data['quantity'] <= 0:
                raise ValidationError({'quantity': 'Must be positive number'})
        serializer.save()

    def perform_destroy(self, instance):
        if instance.is_purchased:
            raise ValidationError({'error': 'Cannot delete purchased items'})
        instance.delete()


class UserViewSet(viewsets.ReadOnlyModelViewSet):
    authentication_classes = [JWTAuthentication]
    queryset = User.objects.all()
    serializer_class = UserSerializer

    def get_permissions(self):
        if self.action in ['list']:
            return [IsAdminUser()]  # Only admins can list all users
        return [IsAuthenticated()]  # Any authenticated user can retrieve their profile

    def get_object(self):
        if self.request.user.is_staff:
            return super().get_object()
        # Non-admin users can only access their own profile
        return self.request.user


class EmailVerificationViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = EmailVerification.objects.all().select_related('user')
    authentication_classes = [JWTAuthentication]
    serializer_class = EmailVerificationSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        if self.request.user.is_staff:
            return EmailVerification.objects.all()
        return EmailVerification.objects.filter(user=self.request.user)

    @action(detail=True, methods=['post'])
    def resend(self, request, pk=None):
        verification = self.get_object()
        verification.send_verification_email()
        return Response({"message": "Verification email resent"}, status=status.HTTP_200_OK)

    @action(detail=True, methods=['post'])
    def verify(self, request, pk=None):
        verification = self.get_object()
        if verification.is_expired():
            return Response(
                {"error": "Verification link has expired"},
                status=status.HTTP_400_BAD_REQUEST
            )
        verification.status = EmailVerificationStatus.VERIFIED.name
        verification.user.is_verified_email = True
        verification.user.save()
        verification.save()
        return Response({"message": "Email verified successfully"})


@extend_schema_view(
    list=extend_schema(
        summary="List all products",
        description="Returns paginated list of all available products",
        parameters=[
            OpenApiParameter(
                name='category',
                type=OpenApiTypes.STR,
                location=OpenApiParameter.QUERY,
                description='Filter by category name',
            ),
        ],
        examples=[
            OpenApiExample(
                'Example response',
                value={
                    "id": 1,
                    "name": "Sample Product",
                    "price": "99.99",
                    "category": "Electronics"
                }
            ),
        ]
    ),
    retrieve=extend_schema(
        summary="Retrieve product details",
        description="Returns complete details for a specific product",
    ),
)
class ProductViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Product.objects.select_related('category')
    serializer_class = ProductSerializer
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def get_permissions(self):
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            return [IsAdminUser()]
        return [IsAuthenticated()]

@extend_schema_view(
    list=extend_schema(
        summary="List all orders",
        description="Returns paginated list of all orders for the authenticated user",
        responses={
            200: OpenApiResponse(
                description="Successful response",
                examples={
                    "application/json": {
                        "id": 1,
                        "status": "CREATED",
                        "total_sum": "99.99"
                    }
                }
            ),
        }
    ),
    retrieve=extend_schema(
        summary="Retrieve order details",
        description="Returns complete details for a specific order",
    ),
)
class OrderViewSet(viewsets.ModelViewSet):
    queryset = Order.objects.all().select_related('initiator').prefetch_related('items')
    serializer_class = OrderSerializer
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Order.objects.filter(
            initiator=self.request.user
        ).select_related('initiator').prefetch_related('items')

    def get_permissions(self):
        if self.action in ['update', 'partial_update', 'destroy']:
            return [IsAuthenticated(), IsOrderOwnerOrAdmin()]
        return [IsAuthenticated()]

    def perform_create(self, serializer):
        baskets = Basket.objects.filter(user=self.request.user, is_purchased=False)
        if not baskets.exists():
            raise ValidationError({"error": "No items in basket to order"})

        order = serializer.save(initiator=self.request.user)
        self._create_order_items(order, baskets)

    def perform_update(self, serializer):
        instance = serializer.instance
        if instance.status != OrderStatus.CREATED:
            raise ValidationError({"error": "Only CREATED orders can be modified"})
        serializer.save()

    def perform_destroy(self, instance):
        if instance.status != OrderStatus.CREATED:
            raise ValidationError({"error": "Only CREATED orders can be canceled"})
        instance.status = OrderStatus.CANCELED
        instance.save()

    def _create_order_items(self, order, baskets):
        order_items = []
        for basket in baskets:
            order_items.append(OrderItem(
                order=order,
                product=basket.product,
                quantity=basket.quantity,
                price=basket.product.price
            ))
            basket.is_purchased = True
            basket.save()
        OrderItem.objects.bulk_create(order_items)
