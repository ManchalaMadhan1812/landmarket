import razorpay
from django.conf import settings
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from datetime import timedelta
from django.utils import timezone

from .models import SubscriptionPlan, UserSubscription, Payment
from .serializers import SubscriptionPlanSerializer, UserSubscriptionSerializer, PaymentSerializer

class SubscriptionPlanViewSet(viewsets.ReadOnlyModelViewSet):
    """
    List available subscription plans
    """
    queryset = SubscriptionPlan.objects.filter(is_active=True).order_by('price')
    serializer_class = SubscriptionPlanSerializer
    permission_classes = [AllowAny]

class PaymentViewSet(viewsets.GenericViewSet):
    """
    Payment and subscription endpoints
    """
    permission_classes = [IsAuthenticated]
    serializer_class = PaymentSerializer

    def get_razorpay_client(self):
        return razorpay.Client(auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET))

    @action(detail=False, methods=['post'])
    def create_order(self, request):
        plan_id = request.data.get('plan_id')
        if not plan_id:
            return Response({'error': 'plan_id is required'}, status=status.HTTP_400_BAD_REQUEST)
            
        try:
            plan = SubscriptionPlan.objects.get(id=plan_id, is_active=True)
        except SubscriptionPlan.DoesNotExist:
            return Response({'error': 'Invalid plan'}, status=status.HTTP_404_NOT_FOUND)

        amount_in_paise = int(plan.price * 100)
        
        client = self.get_razorpay_client()
        try:
            order_data = {
                'amount': amount_in_paise,
                'currency': 'INR',
                'receipt': f'receipt_{request.user.id}_{plan.id}',
                'payment_capture': 1
            }
            order = client.order.create(data=order_data)
            
            # Create a pending Payment record
            payment = Payment.objects.create(
                user=request.user,
                subscription_plan=plan,
                amount=plan.price,
                razorpay_order_id=order['id'],
                status='pending'
            )
            
            return Response({
                'order_id': order['id'],
                'amount': amount_in_paise,
                'currency': 'INR',
                'payment_id': payment.id,
                'key_id': settings.RAZORPAY_KEY_ID
            })
            
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    @action(detail=False, methods=['post'])
    def verify_payment(self, request):
        razorpay_payment_id = request.data.get('razorpay_payment_id')
        razorpay_order_id = request.data.get('razorpay_order_id')
        razorpay_signature = request.data.get('razorpay_signature')
        
        if not all([razorpay_payment_id, razorpay_order_id, razorpay_signature]):
            return Response({'error': 'Missing payment verification details'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            payment = Payment.objects.get(razorpay_order_id=razorpay_order_id, user=request.user)
        except Payment.DoesNotExist:
            return Response({'error': 'Payment record not found'}, status=status.HTTP_404_NOT_FOUND)

        client = self.get_razorpay_client()
        try:
            # Verify signature
            params_dict = {
                'razorpay_order_id': razorpay_order_id,
                'razorpay_payment_id': razorpay_payment_id,
                'razorpay_signature': razorpay_signature
            }
            client.utility.verify_payment_signature(params_dict)
            
            # Mark payment as successful
            payment.razorpay_payment_id = razorpay_payment_id
            payment.razorpay_signature = razorpay_signature
            payment.status = 'successful'
            payment.save()
            
            # Create or update subscription
            plan = payment.subscription_plan
            end_date = timezone.now() + timedelta(days=plan.duration_days)
            
            # Inactivate old subscriptions for this user if they exist? 
            # We'll just create a new one.
            UserSubscription.objects.filter(user=request.user, is_active=True).update(is_active=False)
            
            subscription = UserSubscription.objects.create(
                user=request.user,
                plan=plan,
                end_date=end_date,
                is_active=True
            )
            
            return Response({
                'message': 'Payment verified and subscription activated successfully',
                'subscription': UserSubscriptionSerializer(subscription).data
            })
            
        except razorpay.errors.SignatureVerificationError:
            payment.status = 'failed'
            payment.save()
            return Response({'error': 'Payment verification failed'}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    @action(detail=False, methods=['get'])
    def my_subscription(self, request):
        subscription = UserSubscription.objects.filter(user=request.user, is_active=True, end_date__gt=timezone.now()).first()
        if subscription:
            return Response(UserSubscriptionSerializer(subscription).data)
        return Response({'message': 'No active subscription'}, status=status.HTTP_404_NOT_FOUND)
