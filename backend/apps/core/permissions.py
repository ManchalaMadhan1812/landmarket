"""
Custom permission classes for role-based access control
"""

from rest_framework import permissions
from rest_framework.permissions import BasePermission


class IsOwnerOrReadOnly(BasePermission):
    """
    Custom permission to only allow owners of an object to edit it.
    """

    def has_object_permission(self, request, view, obj):
        # Read permissions are allowed for any request,
        # so we'll always allow GET, HEAD or OPTIONS requests.
        if request.method in permissions.SAFE_METHODS:
            return True

        # Write permissions are only allowed to the owner of the object.
        return obj.owner == request.user


class IsBuyerOrReadOnly(BasePermission):
    """
    Permission for buyer-specific actions
    """
    
    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return True
        return request.user.is_authenticated and request.user.role == 'buyer'


class IsVendorOrReadOnly(BasePermission):
    """
    Permission for vendor-specific actions
    """
    
    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return True
        return request.user.is_authenticated and request.user.role in ['vendor', 'broker']


class IsBrokerOrReadOnly(BasePermission):
    """
    Permission for broker-specific actions
    """
    
    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return True
        return request.user.is_authenticated and request.user.role == 'broker'


class IsAdminUser(BasePermission):
    """
    Permission for admin users only
    """
    
    def has_permission(self, request, view):
        return (
            request.user and 
            request.user.is_authenticated and 
            request.user.role in ['admin', 'super_admin']
        )


class IsVerificationOfficer(BasePermission):
    """
    Permission for verification officers
    """
    
    def has_permission(self, request, view):
        return (
            request.user and 
            request.user.is_authenticated and 
            request.user.role in ['verification_officer', 'admin', 'super_admin']
        )


class IsFinanceManager(BasePermission):
    """
    Permission for finance managers
    """
    
    def has_permission(self, request, view):
        return (
            request.user and 
            request.user.is_authenticated and 
            request.user.role in ['finance_manager', 'super_admin']
        )


class IsPropertyOwnerOrBroker(BasePermission):
    """
    Permission to allow property owners and assigned brokers to modify properties
    """
    
    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True
        
        # Allow property owner
        if hasattr(obj, 'owner') and obj.owner == request.user:
            return True
        
        # Allow assigned broker
        if hasattr(obj, 'broker') and obj.broker == request.user:
            return True
        
        # Allow admin users
        if request.user.role in ['admin', 'super_admin']:
            return True
        
        return False


class CanManageProperty(BasePermission):
    """
    Complex permission for property management
    """
    
    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            return False
        
        # Buyers can only read
        if request.user.role == 'buyer':
            return request.method in permissions.SAFE_METHODS
        
        # Vendors, brokers, and admins can create properties
        return request.user.role in ['vendor', 'broker', 'admin', 'super_admin']
    
    def has_object_permission(self, request, view, obj):
        # Anyone can read active properties
        if request.method in permissions.SAFE_METHODS and obj.status == 'active':
            return True
        
        # Owners can manage their properties
        if hasattr(obj, 'owner') and obj.owner == request.user:
            return True
        
        # Brokers can manage assigned properties
        if hasattr(obj, 'broker') and obj.broker == request.user:
            return True
        
        # Admins can manage any property
        if request.user.role in ['admin', 'super_admin']:
            return True
        
        return False