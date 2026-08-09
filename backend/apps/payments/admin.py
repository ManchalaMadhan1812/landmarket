from django.contrib import admin
from .models import SubscriptionPlan, UserSubscription, Payment

@admin.register(SubscriptionPlan)
class SubscriptionPlanAdmin(admin.ModelAdmin):
    list_display = ('name', 'price', 'duration_days', 'is_active')
    list_filter = ('is_active',)
    search_fields = ('name',)

@admin.register(UserSubscription)
class UserSubscriptionAdmin(admin.ModelAdmin):
    list_display = ('user', 'plan', 'start_date', 'end_date', 'is_active')
    list_filter = ('is_active', 'plan')
    search_fields = ('user__email', 'user__first_name')

@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ('user', 'subscription_plan', 'amount', 'status', 'created_at')
    list_filter = ('status',)
    search_fields = ('user__email', 'razorpay_order_id', 'razorpay_payment_id')
