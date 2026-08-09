"""
Property API views
"""

from rest_framework import viewsets, status, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from django_filters.rest_framework import DjangoFilterBackend
from django.contrib.gis.db.models import Distance
from django.contrib.gis.geos import Point
from django.utils import timezone
from django.db.models import Q, Avg

from apps.core.permissions import (
    CanManageProperty,
    IsAdminUser,
    IsPropertyOwnerOrBroker,
)
from .models import Property, Wishlist, Review, PropertyImage, PropertyDocument
from .serializers import (
    PropertyListSerializer,
    PropertyDetailSerializer,
    PropertyCreateUpdateSerializer,
    WishlistSerializer,
    ReviewSerializer,
    PropertyApprovalSerializer,
)


class PropertyViewSet(viewsets.ModelViewSet):
    """
    Property CRUD and discovery endpoints
    """
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['property_type', 'purpose', 'city', 'status']
    search_fields = ['title', 'description', 'address', 'city']
    ordering_fields = ['price', 'created_at', 'view_count']
    ordering = ['-created_at']

    def get_queryset(self):
        """
        Filter properties based on user and query params
        """
        queryset = Property.objects.select_related('owner', 'broker').prefetch_related('images')

        # Filter by status based on user role
        if self.request.user.role == 'admin':
            # Admins see all properties
            pass
        elif self.request.user.role in ['vendor', 'broker']:
            # Vendors/brokers see their own properties and all active properties
            queryset = queryset.filter(
                Q(owner=self.request.user) | Q(broker=self.request.user) | Q(status='active')
            )
        else:
            # Buyers see only active properties
            queryset = queryset.filter(status='active')

        # Filter by price range
        min_price = self.request.query_params.get('min_price')
        max_price = self.request.query_params.get('max_price')
        if min_price:
            queryset = queryset.filter(price__gte=float(min_price))
        if max_price:
            queryset = queryset.filter(price__lte=float(max_price))

        # Filter by area range
        min_area = self.request.query_params.get('min_area')
        max_area = self.request.query_params.get('max_area')
        if min_area:
            queryset = queryset.filter(total_area__gte=float(min_area))
        if max_area:
            queryset = queryset.filter(total_area__lte=float(max_area))

        # Filter by multiple IDs (e.g. for comparison)
        ids_params = self.request.query_params.getlist('ids')
        if ids_params:
            ids = []
            for param in ids_params:
                ids.extend([i.strip() for i in param.split(',') if i.strip()])
            if ids:
                queryset = queryset.filter(id__in=ids)

        return queryset

    def get_serializer_class(self):
        """Return different serializers based on action"""
        if self.action == 'retrieve':
            return PropertyDetailSerializer
        elif self.action in ['create', 'update', 'partial_update']:
            return PropertyCreateUpdateSerializer
        return PropertyListSerializer

    def get_permissions(self):
        """Set permissions based on action"""
        if self.action in ['create']:
            permission_classes = [IsAuthenticated]
        elif self.action in ['update', 'partial_update', 'destroy']:
            permission_classes = [IsPropertyOwnerOrBroker]
        elif self.action in ['approve', 'reject']:
            permission_classes = [IsAdminUser]
        else:
            permission_classes = [AllowAny]
        return [permission() for permission in permission_classes]

    def perform_create(self, serializer):
        """Create property with owner set to current user"""
        property_obj = serializer.save(owner=self.request.user)
        # Set location if provided in context
        if 'latitude' in self.request.data and 'longitude' in self.request.data:
            property_obj.location = Point(
                float(self.request.data['longitude']),
                float(self.request.data['latitude']),
                srid=4326
            )
            property_obj.save()

    def retrieve(self, request, *args, **kwargs):
        """Increment view count when property is viewed"""
        response = super().retrieve(request, *args, **kwargs)
        self.get_object().increment_view_count()
        return response

    @action(detail=False, methods=['get'])
    def nearby(self, request):
        """
        Get properties near user's location
        Query params: latitude, longitude, radius_km (default: 10)
        """
        latitude = request.query_params.get('latitude')
        longitude = request.query_params.get('longitude')
        radius_km = float(request.query_params.get('radius_km', 10))

        if not latitude or not longitude:
            return Response(
                {'error': 'latitude and longitude are required'},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Create point from coordinates
        user_location = Point(float(longitude), float(latitude), srid=4326)

        # Find properties within radius
        properties = self.get_queryset().annotate(
            distance=Distance('location', user_location)
        ).filter(distance__lte=radius_km * 1000).order_by('distance')

        serializer = self.get_serializer(properties, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def my_listings(self, request):
        """Get current user's property listings"""
        if request.user.role not in ['vendor', 'broker', 'admin']:
            return Response(
                {'error': 'Only vendors and brokers can list properties'},
                status=status.HTTP_403_FORBIDDEN
            )

        queryset = Property.objects.filter(
            Q(owner=request.user) | Q(broker=request.user)
        ).order_by('-created_at')

        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['post'])
    def approve(self, request, pk=None):
        """Approve a property (admin only)"""
        property_obj = self.get_object()
        
        if property_obj.status == 'active':
            return Response(
                {'error': 'Property is already active'},
                status=status.HTTP_400_BAD_REQUEST
            )

        property_obj.status = 'active'
        property_obj.approved_by = request.user
        property_obj.approved_at = timezone.now()
        property_obj.save()

        serializer = self.get_serializer(property_obj)
        return Response({
            'message': 'Property approved successfully',
            'property': serializer.data
        })

    @action(detail=True, methods=['post'])
    def reject(self, request, pk=None):
        """Reject a property (admin only)"""
        property_obj = self.get_object()
        serializer = PropertyApprovalSerializer(data=request.data)

        if serializer.is_valid():
            property_obj.status = 'rejected'
            property_obj.rejection_reason = serializer.validated_data.get('rejection_reason', '')
            property_obj.save()

            return Response({
                'message': 'Property rejected',
                'property': PropertyDetailSerializer(property_obj).data
            })

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=['post'])
    def save_property(self, request, pk=None):
        """Save/wishlist a property"""
        property_obj = self.get_object()

        wishlist, created = Wishlist.objects.get_or_create(
            user=request.user,
            property=property_obj
        )

        if created:
            property_obj.increment_save_count()
            return Response(
                {'message': 'Property saved', 'saved': True},
                status=status.HTTP_201_CREATED
            )
        else:
            return Response(
                {'message': 'Property already in wishlist', 'saved': True},
                status=status.HTTP_200_OK
            )

    @action(detail=True, methods=['post'])
    def unsave_property(self, request, pk=None):
        """Remove property from wishlist"""
        property_obj = self.get_object()

        try:
            wishlist = Wishlist.objects.get(user=request.user, property=property_obj)
            wishlist.delete()

            return Response({'message': 'Property removed from wishlist', 'saved': False})
        except Wishlist.DoesNotExist:
            return Response(
                {'error': 'Property not in wishlist'},
                status=status.HTTP_404_NOT_FOUND
            )


class WishlistViewSet(viewsets.ModelViewSet):
    """
    Wishlist/saved properties endpoint
    """
    serializer_class = WishlistSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Wishlist.objects.filter(user=self.request.user).order_by('-created_at')

    def create(self, request, *args, **kwargs):
        """Save a property"""
        property_id = request.data.get('property_id')
        try:
            property_obj = Property.objects.get(id=property_id, status='active')
        except Property.DoesNotExist:
            return Response(
                {'error': 'Property not found'},
                status=status.HTTP_404_NOT_FOUND
            )

        wishlist, created = Wishlist.objects.get_or_create(
            user=request.user,
            property=property_obj
        )

        serializer = self.get_serializer(wishlist)
        return Response(serializer.data, status=status.HTTP_201_CREATED if created else status.HTTP_200_OK)


class ReviewViewSet(viewsets.ModelViewSet):
    """
    Property reviews endpoint
    """
    serializer_class = ReviewSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Review.objects.all().order_by('-created_at')

    def create(self, request):
        """Create a review for a property"""
        property_id = request.data.get('property_id')
        try:
            property_obj = Property.objects.get(id=property_id)
        except Property.DoesNotExist:
            return Response(
                {'error': 'Property not found'},
                status=status.HTTP_404_NOT_FOUND
            )

        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            serializer.save(
                buyer=request.user,
                property=property_obj,
                vendor=property_obj.owner
            )
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)