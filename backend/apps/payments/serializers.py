from rest_framework import serializers
from .models import SubscriptionPlan, UserSubscription, Payment

class SubscriptionPlanSerializer(serializers.ModelSerializer):
    class Meta:
        model = SubscriptionPlan
        fields = '__all__'

class UserSubscriptionSerializer(serializers.ModelSerializer):
    plan_details = SubscriptionPlanSerializer(source='plan', read_only=True)
    
    class Meta:
        model = UserSubscription
        fields = '__all__'
        read_only_fields = ('user',)

class PaymentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Payment
        fields = '__all__'
        read_only_fields = ('user', 'status', 'razorpay_order_id', 'razorpay_payment_id', 'razorpay_signature')
