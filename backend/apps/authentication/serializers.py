"""
Authentication serializers for API endpoints
"""

from rest_framework import serializers
from django.contrib.auth import authenticate
from django.contrib.auth.password_validation import validate_password
from .models import User, UserProfile


class UserRegistrationSerializer(serializers.ModelSerializer):
    """
    Serializer for user registration
    """
    password = serializers.CharField(write_only=True, validators=[validate_password])
    confirm_password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = [
            'email', 'first_name', 'last_name', 'phone', 'role',
            'password', 'confirm_password'
        ]

    def validate(self, attrs):
        if attrs['password'] != attrs['confirm_password']:
            raise serializers.ValidationError("Passwords don't match")
        return attrs

    def validate_email(self, value):
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError("A user with this email already exists")
        return value

    def validate_phone(self, value):
        if value and User.objects.filter(phone=value).exists():
            raise serializers.ValidationError("A user with this phone number already exists")
        return value

    def create(self, validated_data):
        validated_data.pop('confirm_password')
        password = validated_data.pop('password')
        
        user = User(**validated_data)
        user.set_password(password)
        user.save()
        
        # Create user profile
        UserProfile.objects.create(user=user)
        
        return user


class UserLoginSerializer(serializers.Serializer):
    """
    Serializer for user login
    """
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)

    def validate(self, attrs):
        email = attrs.get('email')
        password = attrs.get('password')

        if email and password:
            user = authenticate(
                request=self.context.get('request'),
                username=email,
                password=password
            )

            if not user:
                raise serializers.ValidationError('Invalid email or password')

            if not user.is_active:
                raise serializers.ValidationError('User account is disabled')

            attrs['user'] = user
            return attrs

        raise serializers.ValidationError('Must include email and password')


class UserSerializer(serializers.ModelSerializer):
    """
    Serializer for user data
    """
    full_name = serializers.CharField(read_only=True)

    class Meta:
        model = User
        fields = [
            'id', 'email', 'first_name', 'last_name', 'full_name',
            'phone', 'role', 'is_verified', 'created_at', 'last_login'
        ]
        read_only_fields = ['id', 'created_at', 'is_verified']


class UserProfileSerializer(serializers.ModelSerializer):
    """
    Serializer for user profile
    """
    user = UserSerializer(read_only=True)
    latitude = serializers.SerializerMethodField()
    longitude = serializers.SerializerMethodField()

    class Meta:
        model = UserProfile
        fields = [
            'user', 'avatar', 'bio', 'city', 'state', 'latitude', 'longitude',
            'preferences', 'verification_score', 'is_identity_verified',
            'is_phone_verified', 'is_email_verified'
        ]

    def get_latitude(self, obj):
        return obj.location.y if obj.location else None

    def get_longitude(self, obj):
        return obj.location.x if obj.location else None


class UpdateLocationSerializer(serializers.Serializer):
    """
    Serializer for updating user location
    """
    latitude = serializers.FloatField(min_value=-90, max_value=90)
    longitude = serializers.FloatField(min_value=-180, max_value=180)
    city = serializers.CharField(max_length=100, required=False)
    state = serializers.CharField(max_length=100, required=False)


class ChangePasswordSerializer(serializers.Serializer):
    """
    Serializer for changing user password
    """
    old_password = serializers.CharField(write_only=True)
    new_password = serializers.CharField(write_only=True, validators=[validate_password])
    confirm_password = serializers.CharField(write_only=True)

    def validate(self, attrs):
        if attrs['new_password'] != attrs['confirm_password']:
            raise serializers.ValidationError("New passwords don't match")
        return attrs

    def validate_old_password(self, value):
        user = self.context['request'].user
        if not user.check_password(value):
            raise serializers.ValidationError("Old password is incorrect")
        return value


class ForgotPasswordSerializer(serializers.Serializer):
    """
    Serializer for forgot password request
    """
    email = serializers.EmailField()

    def validate_email(self, value):
        if not User.objects.filter(email=value).exists():
            raise serializers.ValidationError("No user found with this email address")
        return value


class ResetPasswordSerializer(serializers.Serializer):
    """
    Serializer for password reset
    """
    token = serializers.CharField()
    new_password = serializers.CharField(validators=[validate_password])
    confirm_password = serializers.CharField()

    def validate(self, attrs):
        if attrs['new_password'] != attrs['confirm_password']:
            raise serializers.ValidationError("Passwords don't match")
        return attrs


class UpdateProfileSerializer(serializers.ModelSerializer):
    """
    Serializer for updating user profile
    """
    first_name = serializers.CharField(source='user.first_name')
    last_name = serializers.CharField(source='user.last_name')
    phone = serializers.CharField(source='user.phone', required=False)

    class Meta:
        model = UserProfile
        fields = [
            'first_name', 'last_name', 'phone', 'bio', 'city', 'state', 'avatar'
        ]

    def update(self, instance, validated_data):
        # Update user fields
        user_data = validated_data.pop('user', {})
        user = instance.user
        
        for attr, value in user_data.items():
            setattr(user, attr, value)
        user.save()

        # Update profile fields
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()

        return instance