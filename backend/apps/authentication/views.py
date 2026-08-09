"""
Authentication API views
"""

from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.views import TokenObtainPairView
from django.utils import timezone
from datetime import timedelta

from .models import User, UserProfile
from .serializers import (
    UserRegistrationSerializer,
    UserLoginSerializer,
    UserSerializer,
    UserProfileSerializer,
    UpdateLocationSerializer,
    ChangePasswordSerializer,
    ForgotPasswordSerializer,
    UpdateProfileSerializer,
)


class RegisterView(viewsets.ViewSet):
    """
    User registration endpoint
    """
    permission_classes = [AllowAny]

    def create(self, request):
        serializer = UserRegistrationSerializer(data=request.data)
        
        if serializer.is_valid():
            user = serializer.save()
            refresh = RefreshToken.for_user(user)
            
            return Response({
                'message': 'User registered successfully',
                'user': UserSerializer(user).data,
                'access': str(refresh.access_token),
                'refresh': str(refresh),
            }, status=status.HTTP_201_CREATED)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class LoginView(viewsets.ViewSet):
    """
    User login endpoint
    """
    permission_classes = [AllowAny]

    def create(self, request):
        serializer = UserLoginSerializer(
            data=request.data,
            context={'request': request}
        )
        
        if serializer.is_valid():
            user = serializer.validated_data['user']
            
            # Update last login
            user.last_login = timezone.now()
            user.save(update_fields=['last_login'])
            
            refresh = RefreshToken.for_user(user)
            
            return Response({
                'message': 'Login successful',
                'user': UserSerializer(user).data,
                'access': str(refresh.access_token),
                'refresh': str(refresh),
            }, status=status.HTTP_200_OK)
        
        return Response(serializer.errors, status=status.HTTP_401_UNAUTHORIZED)


class UserProfileViewSet(viewsets.ModelViewSet):
    """
    User profile API endpoint
    """
    serializer_class = UserProfileSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return UserProfile.objects.filter(user=self.request.user)

    def list(self, request):
        """Get current user's profile"""
        try:
            profile = request.user.profile
        except UserProfile.DoesNotExist:
            profile = UserProfile.objects.create(user=request.user)
        
        serializer = self.get_serializer(profile)
        return Response(serializer.data)

    @action(detail=False, methods=['post'])
    def update_location(self, request):
        """Update user location"""
        serializer = UpdateLocationSerializer(data=request.data)
        
        if serializer.is_valid():
            profile = request.user.profile
            profile.update_location(
                serializer.validated_data['latitude'],
                serializer.validated_data['longitude']
            )
            
            if 'city' in serializer.validated_data:
                profile.city = serializer.validated_data['city']
            if 'state' in serializer.validated_data:
                profile.state = serializer.validated_data['state']
            
            profile.save()
            
            return Response({
                'message': 'Location updated successfully',
                'profile': UserProfileSerializer(profile).data
            }, status=status.HTTP_200_OK)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=['patch'])
    def update_profile(self, request):
        """Update user profile"""
        try:
            profile = request.user.profile
        except UserProfile.DoesNotExist:
            profile = UserProfile.objects.create(user=request.user)
        
        serializer = UpdateProfileSerializer(profile, data=request.data, partial=True)
        
        if serializer.is_valid():
            serializer.save()
            return Response({
                'message': 'Profile updated successfully',
                'profile': UserProfileSerializer(profile).data
            }, status=status.HTTP_200_OK)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class CurrentUserView(viewsets.ViewSet):
    """
    Get current authenticated user
    """
    permission_classes = [IsAuthenticated]

    @action(detail=False, methods=['get'])
    def me(self, request):
        """Get current user info"""
        serializer = UserSerializer(request.user)
        return Response(serializer.data)

    @action(detail=False, methods=['post'])
    def change_password(self, request):
        """Change user password"""
        serializer = ChangePasswordSerializer(
            data=request.data,
            context={'request': request}
        )
        
        if serializer.is_valid():
            user = request.user
            user.set_password(serializer.validated_data['new_password'])
            user.save()
            
            # Invalidate all existing tokens by forcing re-login
            refresh = RefreshToken.for_user(user)
            
            return Response({
                'message': 'Password changed successfully',
                'access': str(refresh.access_token),
                'refresh': str(refresh),
            }, status=status.HTTP_200_OK)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=['post'])
    def logout(self, request):
        """Logout user"""
        try:
            refresh_token = request.data.get('refresh')
            token = RefreshToken(refresh_token)
            token.blacklist()
            
            return Response(
                {'message': 'Logout successful'},
                status=status.HTTP_200_OK
            )
        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )


class ForgotPasswordView(viewsets.ViewSet):
    """
    Forgot password endpoint
    """
    permission_classes = [AllowAny]

    def create(self, request):
        """Request password reset"""
        serializer = ForgotPasswordSerializer(data=request.data)
        
        if serializer.is_valid():
            email = serializer.validated_data['email']
            # TODO: Generate reset token and send email
            
            return Response({
                'message': 'If an account exists with this email, a password reset link will be sent'
            }, status=status.HTTP_200_OK)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)