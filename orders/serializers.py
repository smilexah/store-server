from rest_framework import serializers
from products.serializers import BasketSerializer

class OrderSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    first_name = serializers.CharField(max_length=64)
    last_name = serializers.CharField(max_length=64)
    email = serializers.EmailField()
    address = serializers.CharField(max_length=256)
    basket_history = BasketSerializer(many=True, read_only=True)
    status = serializers.IntegerField()
    created = serializers.DateTimeField()
    initiator = serializers.IntegerField()

    def validate_email(self, value):
        if not value or '@' not in value:
            raise serializers.ValidationError("Invalid email address")
        return value

    def validate_address(self, value):
        if not value:
            raise serializers.ValidationError("Address cannot be empty")
        return value

    def validate_basket_history(self, value):
        if not value or len(value) == 0:
            raise serializers.ValidationError("Basket history must contain at least one item.")
        return value
