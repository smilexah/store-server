from rest_framework import fields, serializers

from products.models import Basket, Product, ProductCategory


class ProductSerializer(serializers.ModelSerializer):
    category = serializers.SlugRelatedField(
        slug_field='name',
        queryset=ProductCategory.objects.all(),
        required=False
    )

    name = serializers.CharField(required=False, allow_blank=True)
    description = serializers.CharField(required=False, allow_blank=True)
    price = serializers.DecimalField(
        required=False,
        max_digits=10,
        decimal_places=2,
        allow_null=True
    )
    quantity = serializers.IntegerField(required=False)  # Optional quantity

    class Meta:
        model = Product
        fields = ('id', 'name', 'description', 'price', 'quantity', 'image', 'category')


class BasketSerializer(serializers.ModelSerializer):
    product = ProductSerializer()
    sum = fields.FloatField(required=False)
    total_sum = fields.SerializerMethodField()
    total_quantity = fields.SerializerMethodField()

    class Meta:
        model = Basket
        fields = ('id', 'product', 'quantity', 'sum', 'total_sum', 'total_quantity', 'created_timestamp')
        read_only_fields = ('created_timestamp',)

    def get_total_sum(self, obj):
        return Basket.objects.filter(user_id=obj.user.id).total_sum()

    def get_total_quantity(self, obj):
        return Basket.objects.filter(user_id=obj.user.id).total_quantity()
