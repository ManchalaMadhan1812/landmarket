import React from 'react';
import { useParams, Link } from 'react-router-dom';
import { Helmet } from 'react-helmet-async';
import { useCompareStore } from '../stores/compareStore';
import EmiLandCalculator from '../components/calculator/EmiLandCalculator';
import DocumentVerificationSystem from '../components/verification/DocumentVerificationSystem';
import { ScaleIcon, CheckIcon, PlusIcon, ArrowLeftIcon, CalculatorIcon, ShieldCheckIcon } from '@heroicons/react/24/outline';
import toast from 'react-hot-toast';

const PropertyDetailPage: React.FC = () => {
  const { id } = useParams<{ id: string }>();
  const { addProperty, removeProperty, isComparing } = useCompareStore();
  const currentlyComparing = id ? isComparing(id) : false;

  const handleCompareClick = () => {
    if (!id) return;
    if (currentlyComparing) {
      removeProperty(id);
      toast.success('Removed from comparison');
    } else {
      addProperty(id);
      toast.success('Added to comparison bar');
    }
  };

  return (
    <>
      <Helmet>
        <title>Property Details - LandMarket</title>
      </Helmet>

      <div className="min-h-screen bg-gray-50 py-8">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 space-y-10">
          <div className="flex items-center justify-between">
            <Link to="/search" className="inline-flex items-center gap-2 text-sm text-gray-600 hover:text-gray-900 bg-white px-4 py-2 rounded-xl border border-gray-200 shadow-sm">
              <ArrowLeftIcon className="w-4 h-4" />
              <span>Back to Search</span>
            </Link>

            {id && (
              <div className="flex items-center gap-3">
                <button
                  onClick={handleCompareClick}
                  className={`inline-flex items-center gap-2 px-4 py-2 rounded-xl text-sm font-semibold border transition-all ${
                    currentlyComparing
                      ? 'bg-primary-50 text-primary-700 border-primary-300'
                      : 'bg-white text-gray-700 border-gray-300 hover:bg-gray-50'
                  }`}
                >
                  {currentlyComparing ? (
                    <>
                      <CheckIcon className="w-4 h-4 text-primary-600" />
                      <span>Added to Compare</span>
                    </>
                  ) : (
                    <>
                      <PlusIcon className="w-4 h-4" />
                      <span>Add to Compare</span>
                    </>
                  )}
                </button>

                <Link
                  to="/compare"
                  className="inline-flex items-center gap-2 px-4 py-2 bg-primary-600 hover:bg-primary-700 text-white rounded-xl text-sm font-semibold shadow-sm transition-colors"
                >
                  <ScaleIcon className="w-4 h-4" />
                  <span>View Compare Matrix</span>
                </Link>
              </div>
            )}
          </div>

          {/* Property Summary Header Box */}
          <div className="bg-white rounded-2xl p-8 border border-gray-200 shadow-sm flex flex-col md:flex-row items-center justify-between gap-6">
            <div>
              <span className="text-xs font-bold uppercase tracking-wider text-primary-700 bg-primary-50 px-3 py-1 rounded-full">
                Listing ID: {id?.slice(0, 8)}...
              </span>
              <h1 className="text-2xl sm:text-3xl font-extrabold text-gray-900 mt-2">
                Prime Residential Plot / Land Property
              </h1>
              <p className="text-sm text-gray-500 mt-1">
                Chennai, Tamil Nadu • Total Area: 2,400 Ground / Sq Ft
              </p>
            </div>
            <div className="text-right">
              <span className="text-xs text-gray-400 font-medium block">Listed Price</span>
              <span className="text-3xl font-extrabold text-primary-700">₹75,000,00</span>
            </div>
          </div>

          {/* Integrated Document Verification & Legal Trust System */}
          <div className="space-y-4">
            <div className="flex items-center gap-2 text-gray-900 font-bold text-xl">
              <ShieldCheckIcon className="w-6 h-6 text-primary-600" />
              <span>Legal Document Verification & Trust Audit</span>
            </div>
            <DocumentVerificationSystem />
          </div>

          {/* Integrated Mortgage EMI & Land Converter Section */}
          <div className="space-y-4">
            <div className="flex items-center gap-2 text-gray-900 font-bold text-xl">
              <CalculatorIcon className="w-6 h-6 text-primary-600" />
              <span>Financial EMI Calculator & Unit Converter</span>
            </div>
            <EmiLandCalculator initialPrice={7500000} initialArea={2400} initialAreaUnit="sqft" />
          </div>
        </div>
      </div>
    </>
  );
};

export default PropertyDetailPage;