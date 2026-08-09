import React from 'react';
import { Helmet } from 'react-helmet-async';
import { Link } from 'react-router-dom';
import EmiLandCalculator from '../components/calculator/EmiLandCalculator';
import { CalculatorIcon, ArrowLeftIcon, SparklesIcon, InformationCircleIcon } from '@heroicons/react/24/outline';

const CalculatorPage: React.FC = () => {
  return (
    <>
      <Helmet>
        <title>Land & Home Loan EMI Calculator - LandMarket</title>
      </Helmet>

      <div className="min-h-screen bg-gray-50 py-8">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          {/* Header */}
          <div className="flex items-center gap-4 mb-8">
            <Link
              to="/search"
              className="p-2.5 bg-white border border-gray-200 rounded-xl hover:bg-gray-50 text-gray-700 shadow-sm transition-colors"
            >
              <ArrowLeftIcon className="w-5 h-5" />
            </Link>
            <div>
              <div className="flex items-center gap-2 text-xs font-bold uppercase tracking-wider text-primary-700 mb-1">
                <SparklesIcon className="w-4 h-4" />
                <span>Financial & Geospatial Tools</span>
              </div>
              <h1 className="text-3xl font-extrabold text-gray-900">Land & Home Loan EMI Calculator</h1>
            </div>
          </div>

          {/* Calculator Widget Component */}
          <div className="mb-12">
            <EmiLandCalculator />
          </div>

          {/* Educational Land Metrics Reference Guide */}
          <div className="bg-white rounded-2xl border border-gray-200 p-6 sm:p-8 shadow-sm">
            <div className="flex items-center gap-2 mb-4 text-gray-900 font-bold text-lg">
              <InformationCircleIcon className="w-5 h-5 text-primary-600" />
              <span>Understanding Indian Land Measurement Units</span>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-3 gap-6 text-xs sm:text-sm text-gray-600">
              <div className="bg-gray-50 p-4 rounded-xl border border-gray-100">
                <h4 className="font-bold text-gray-900 mb-1">South India Metrics</h4>
                <p>
                  In Tamil Nadu and Kerala, <strong>Cent</strong> and <strong>Ground</strong> are standard. 1 Cent equals 435.6 sq ft, and 1 Ground equals 2,400 sq ft (6 Cents).
                </p>
              </div>

              <div className="bg-gray-50 p-4 rounded-xl border border-gray-100">
                <h4 className="font-bold text-gray-900 mb-1">Western & Central India</h4>
                <p>
                  In Maharashtra, Gujarat, and Karnataka, land is often measured in <strong>Guntha</strong> (1,089 sq ft). 40 Gunthas equal 1 Acre.
                </p>
              </div>

              <div className="bg-gray-50 p-4 rounded-xl border border-gray-100">
                <h4 className="font-bold text-gray-900 mb-1">North & Eastern India</h4>
                <p>
                  <strong>Bigha</strong> is traditionally used across Uttar Pradesh, Bihar, and Punjab. 1 Standard Bigha is approximately 27,225 sq ft.
                </p>
              </div>
            </div>
          </div>
        </div>
      </div>
    </>
  );
};

export default CalculatorPage;
