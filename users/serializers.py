from rest_framework import serializers
from .models import User
from django.core.validators import EmailValidator

class EmailVerificationSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    user = serializers.IntegerField()
    code = serializers.UUIDField()
    created = serializers.DateTimeField()
    expiration = serializers.DateTimeField()
    status = serializers.CharField(max_length=50)

class UserSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    username = serializers.CharField(max_length=150)
    email = serializers.EmailField()
    image = serializers.ImageField(required=False)
    is_verified_email = serializers.BooleanField()
    full_name = serializers.SerializerMethodField()
    email_verification = EmailVerificationSerializer(source='emailverification_set', many=True, read_only=True)

    def get_full_name(self, obj):
        return f'{obj.first_name} {obj.last_name}'

    def validate_email(self, value):
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError("Email is already in use.")
        EmailValidator()(value)
        return value

    def validate_username(self, value):
        if User.objects.filter(username=value).exists():
            raise serializers.ValidationError("Username is already taken.")
        if not value:
            raise serializers.ValidationError("Username cannot be empty.")
        return value

    def validate_image(self, value):
        if value:
            if value.size > 5 * 1024 * 1024:  # 5 MB limit
                raise serializers.ValidationError("Image file size should not exceed 5 MB.")
        return value
