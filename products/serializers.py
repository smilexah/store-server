from rest_framework import serializers
from products.models import Basket, Product, ProductCategory


class ProductSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    name = serializers.CharField(required=True, allow_blank=False)
    description = serializers.CharField(required=False, allow_blank=True)
    price = serializers.DecimalField(required=True, max_digits=10, decimal_places=2)
    quantity = serializers.IntegerField(required=True, min_value=0)
    image = serializers.ImageField(required=False)
    category = serializers.SlugRelatedField(slug_field='name', queryset=ProductCategory.objects.all(), required=False)

    def validate_price(self, value):
        if value <= 0:
            raise serializers.ValidationError("Price must be a positive number")
        return value

    def validate_quantity(self, value):
        if value < 0:
            raise serializers.ValidationError("Quantity must be a non-negative integer")
        return value

    def validate_name(self, value):
        if not value:
            raise serializers.ValidationError("Product name cannot be empty")
        return value

    def validate_category(self, value):
        if value and not ProductCategory.objects.filter(name=value).exists():
            raise serializers.ValidationError("Category does not exist")
        return value

    class Meta:
        model = Product
        fields = '__all__'

        swagger_schema = {
            'title': 'Product',
            'description': 'Product details including name, description, price, quantity, and category.',
            'type': 'object',
            'properties': {
                'id': {'type': 'integer', 'description': 'Product ID'},
                'name': {'type': 'string', 'description': 'Product name'},
                'description': {'type': 'string', 'description': 'Product description'},
                'price': {'type': 'number', 'format': 'float', 'description': 'Product price'},
                'quantity': {'type': 'integer', 'description': 'Available quantity of the product'},
                'image': {'type': ['string', 'null'], 'format': 'binary',
                          'description': "Product image (optional)"},
                'category': {'type': ['string', 'null'],
                             "description": "Category name (optional)"}
            },
        }


class BasketSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    product = ProductSerializer()
    quantity = serializers.IntegerField(min_value=1)
    sum = serializers.FloatField(required=False)
    total_sum = serializers.SerializerMethodField()
    total_quantity = serializers.SerializerMethodField()
    product_details = serializers.SerializerMethodField()

    def validate_quantity(self, value):
        if value <= 0:
            raise serializers.ValidationError("Quantity must be greater than zero")
        return value

    def validate_product(self, value):
        if not Product.objects.filter(id=value.id).exists():
            raise serializers.ValidationError("Product does not exist")
        return value

    def get_total_sum(self, obj):
        total_sum = Basket.objects.filter(user=obj.user).total_sum()
        return total_sum

    def get_total_quantity(self, obj):
        total_quantity = Basket.objects.filter(user=obj.user).total_quantity()
        return total_quantity

    # Get product details
    def get_product_details(self, obj):
        return {
            'product_name': obj.product.name,
            'product_price': obj.product.price
        }
