import React, { useEffect, useState } from 'react';
import { Helmet } from 'react-helmet-async';
import { useQuery } from '@tanstack/react-query';
import { CheckIcon } from '@heroicons/react/24/solid';
import toast from 'react-hot-toast';
import { useNavigate } from 'react-router-dom';

import LoadingSpinner from '../components/ui/LoadingSpinner';
import { getSubscriptionPlans, createRazorpayOrder, verifyRazorpayPayment, SubscriptionPlan } from '../services/paymentService';
import { loadRazorpayScript } from '../utils/razorpay';
import { useAuthStore } from '../stores/authStore';

const PricingPage: React.FC = () => {
  const { user, isAuthenticated } = useAuthStore();
  const navigate = useNavigate();
  const [processingPlanId, setProcessingPlanId] = useState<string | null>(null);

  const { data: plans, isLoading, error } = useQuery<SubscriptionPlan[]>({
    queryKey: ['subscriptionPlans'],
    queryFn: getSubscriptionPlans,
  });

  const handleSubscribe = async (plan: SubscriptionPlan) => {
    if (!isAuthenticated || !user) {
      toast.error('Please login to subscribe to a plan');
      navigate('/auth/login', { state: { returnTo: '/pricing' } });
      return;
    }

    setProcessingPlanId(plan.id);

    try {
      const isScriptLoaded = await loadRazorpayScript();
      if (!isScriptLoaded) {
        toast.error('Failed to load Razorpay SDK. Please check your connection.');
        setProcessingPlanId(null);
        return;
      }

      // Create order on backend
      const orderData = await createRazorpayOrder(plan.id);
      
      const options = {
        key: orderData.key_id,
        amount: orderData.amount,
        currency: orderData.currency,
        name: 'LandMarket',
        description: `Subscription to ${plan.name} Plan`,
        image: '/icon-192x192.png',
        order_id: orderData.order_id,
        handler: async function (response: any) {
          try {
            await verifyRazorpayPayment(
              response.razorpay_payment_id,
              response.razorpay_order_id,
              response.razorpay_signature
            );
            toast.success('Subscription activated successfully!');
            navigate('/app/dashboard');
          } catch (err: any) {
            toast.error(err.message || 'Payment verification failed');
          }
        },
        prefill: {
          name: `${user.firstName} ${user.lastName}`.trim(),
          email: user.email,
          contact: user.phone || '',
        },
        theme: {
          color: '#4F46E5', // primary-600
        },
      };

      const rzp = new (window as any).Razorpay(options);
      
      rzp.on('payment.failed', function (response: any) {
        toast.error(response.error.description || 'Payment failed');
      });

      rzp.open();
    } catch (err: any) {
      toast.error(err.message || 'Failed to initialize payment');
    } finally {
      setProcessingPlanId(null);
    }
  };

  return (
    <>
      <Helmet>
        <title>Pricing Plans - LandMarket</title>
      </Helmet>

      <div className="bg-white py-24 sm:py-32">
        <div className="mx-auto max-w-7xl px-6 lg:px-8">
          <div className="mx-auto max-w-4xl text-center">
            <h2 className="text-base font-semibold leading-7 text-primary-600">Pricing</h2>
            <p className="mt-2 text-4xl font-bold tracking-tight text-gray-900 sm:text-5xl">
              Pricing plans for everyone
            </p>
          </div>
          <p className="mx-auto mt-6 max-w-2xl text-center text-lg leading-8 text-gray-600">
            Choose an affordable plan that's packed with the best features for engaging your audience, creating customer loyalty, and driving sales.
          </p>

          {isLoading ? (
            <div className="mt-16 flex justify-center">
              <LoadingSpinner size="lg" />
            </div>
          ) : error ? (
            <div className="mt-16 text-center text-red-600">
              Failed to load pricing plans. Please try again later.
            </div>
          ) : (
            <div className="isolate mx-auto mt-16 grid max-w-md grid-cols-1 gap-y-8 sm:mt-20 lg:mx-0 lg:max-w-none lg:grid-cols-3 lg:gap-x-8 lg:gap-y-0">
              {plans?.map((plan, planIdx) => (
                <div
                  key={plan.id}
                  className={`rounded-3xl p-8 ring-1 xl:p-10 ${
                    planIdx === 1 ? 'bg-gray-900 ring-gray-900' : 'ring-gray-200'
                  }`}
                >
                  <h3
                    id={plan.id}
                    className={`text-lg font-semibold leading-8 ${
                      planIdx === 1 ? 'text-white' : 'text-gray-900'
                    }`}
                  >
                    {plan.name}
                  </h3>
                  <p
                    className={`mt-4 text-sm leading-6 ${
                      planIdx === 1 ? 'text-gray-300' : 'text-gray-600'
                    }`}
                  >
                    {plan.description}
                  </p>
                  <p className="mt-6 flex items-baseline gap-x-1">
                    <span
                      className={`text-4xl font-bold tracking-tight ${
                        planIdx === 1 ? 'text-white' : 'text-gray-900'
                      }`}
                    >
                      ₹{plan.price}
                    </span>
                    <span
                      className={`text-sm font-semibold leading-6 ${
                        planIdx === 1 ? 'text-gray-300' : 'text-gray-600'
                      }`}
                    >
                      /{plan.duration_days} days
                    </span>
                  </p>
                  <button
                    onClick={() => handleSubscribe(plan)}
                    disabled={processingPlanId === plan.id}
                    aria-describedby={plan.id}
                    className={`mt-6 block rounded-md py-2 px-3 text-center text-sm font-semibold leading-6 focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 w-full ${
                      planIdx === 1
                        ? 'bg-white text-gray-900 hover:bg-gray-100 focus-visible:outline-white'
                        : 'bg-primary-600 text-white hover:bg-primary-700 focus-visible:outline-primary-600'
                    } ${processingPlanId === plan.id ? 'opacity-70 cursor-not-allowed' : ''}`}
                  >
                    {processingPlanId === plan.id ? 'Processing...' : 'Subscribe'}
                  </button>
                  <ul
                    role="list"
                    className={`mt-8 space-y-3 text-sm leading-6 xl:mt-10 ${
                      planIdx === 1 ? 'text-gray-300' : 'text-gray-600'
                    }`}
                  >
                    {plan.features.map((feature: string, index: number) => (
                      <li key={index} className="flex gap-x-3">
                        <CheckIcon
                          className={`h-6 w-5 flex-none ${
                            planIdx === 1 ? 'text-white' : 'text-primary-600'
                          }`}
                          aria-hidden="true"
                        />
                        {feature}
                      </li>
                    ))}
                  </ul>
                </div>
              ))}
            </div>
          )}
        </div>
      </div>
    </>
  );
};

export default PricingPage;
