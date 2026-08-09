import api from './api';

export interface SubscriptionPlan {
  id: string;
  name: string;
  description: string;
  price: string | number;
  duration_days: number;
  features: string[];
  is_active: boolean;
}

export interface UserSubscription {
  id: string;
  user: number;
  plan: string;
  plan_details: SubscriptionPlan;
  start_date: string;
  end_date: string;
  is_active: boolean;
}

export const getSubscriptionPlans = async (): Promise<SubscriptionPlan[]> => {
  const response = await api.get('/api/subscriptions/plans/');
  return response.data;
};

export const createRazorpayOrder = async (planId: string) => {
  const response = await api.post('/api/subscriptions/payments/create_order/', { plan_id: planId });
  return response.data;
};

export const verifyRazorpayPayment = async (
  razorpayPaymentId: string,
  razorpayOrderId: string,
  razorpaySignature: string
) => {
  const response = await api.post('/api/subscriptions/payments/verify_payment/', {
    razorpay_payment_id: razorpayPaymentId,
    razorpay_order_id: razorpayOrderId,
    razorpay_signature: razorpaySignature,
  });
  return response.data;
};

export const getMySubscription = async (): Promise<UserSubscription> => {
  const response = await api.get('/api/subscriptions/payments/my_subscription/');
  return response.data;
};
